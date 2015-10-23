# -*- coding: utf-8 -*-

import yaml
import pytest
import requests

GI_API_URL = 'https://api.ghostinspector.com/v1/'


# Command-line Options

def pytest_addoption(parser):
    group = parser.getgroup('ghostinspector')
    group.addoption(
        '--gi_key',
        action='store',
        dest='gi_key',
        help='Set the value for the Ghost Inspector API key'
    )
    group.addoption(
        '--gi_start_url',
        action='store',
        dest='gi_start_url',
        help='Override the starting url value for the Ghost Inspector tests'
    )

    parser.addini('gi_key', 'Dummy pytest.ini setting')


# Plugin hook impls

def pytest_configure(config):
    """Configuration hook to verify we got the necessary options"""
    if not config.option.help and config.option.gi_key is None:
        raise pytest.UsageError("Missing --gi_key option")

def pytest_collect_file(path, parent):
    """Collection hook for ghost inspector tests

    This looks for yaml files containing configuration info for executing
    http://ghostinspector.com tests via the API
    """
    if str(path.basename.startswith('gi_test_')) and path.ext == '.yml':
        return GICollector(path, parent=parent)

class GIAPIMixin(object):

    def _api_request(self, url, params=None):
        if params is None:
            params = {}
        params['apiKey'] = self.gi_key
        if self.config.option.gi_start_url is not None:
            params['startUrl'] = self.config.option.gi_start_url
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()['data']


class GICollector(pytest.File, GIAPIMixin):
    """Collect and generate pytest test items based on yaml config"""

    def __init__(self, *args, **kwargs):
        super(GICollector, self).__init__(*args, **kwargs)
        self.gi_key = self.config.option.gi_key
        self.gi_param_options = []

    def collect(self):
        raw = yaml.safe_load(self.fspath.open())

        # globally set test execution params
        if 'param_options' in raw:
            self.gi_param_options = raw['param_options']

        for suite in raw.get('suites', []):
            for test_item in self._collect_suite(suite):
                yield test_item

        for test in raw.get('tests', []):
            yield self._collect_test(test)

    def _collect_suite(self, suite):
        url = GI_API_URL + 'suites/{}/tests/'.format(suite['id'])
        test_list = self._api_request(url)
        for test in test_list:
            spec = {
                'id': test['_id'],
                'suite': test['suite']['name'],
                'params': self._spec_param_opts(suite)
            }
            yield GITestItem(test['name'], self, spec)

    def _collect_test(self, test):
        url = GI_API_URL + 'tests/{}/'.format(test['id'])
        test_data = self._api_request(url)
        spec = {
            'id': test_data['_id'],
            'suite': test_data['suite']['name'],
            'params': self._spec_param_opts(test)
        }
        return GITestItem(test_data['name'], self, spec)

    def _spec_param_opts(self, node):
        spec_params = {}
        param_opts = self.gi_param_options
        if 'param_options' in node:
            param_opts.extend(node['param_options'])
        for param_opt in param_opts:
            try:
                spec_params[param_opt] = getattr(self.config.option, 'gi_' + param_opt)
            except AttributeError:
                raise pytest.UsageError(
                    "Unknown command-line option specified in param_options: gi_%s" % param_opt)
        return spec_params

class GITestItem(pytest.Item, GIAPIMixin):

    def __init__(self, name, parent, spec):
        super(GITestItem, self).__init__(name, parent)
        self.gi_key = self.config.option.gi_key
        self.spec = spec

    def runtest(self):
        url = GI_API_URL + 'tests/{}/execute/'.format(self.spec['id'])
        result = self._api_request(url, self.spec['params'])
        if not result['passing']:
            raise GIException(self, result)

    def repr_failure(self, excinfo):
        """ format failure info from GI API response """
        if isinstance(excinfo.value, GIException):
            resp_data = excinfo.value.args[1]
            failing_step = next(step for step in resp_data['steps'] if not step['passing'])
            return "\n".join([
                "Ghost Inspector test failed",
                "   name: %s" % resp_data['test']['name'],
                "   result url: https://app.ghostinspector.com/results/%s" % resp_data['_id'],
                "   step #: %d" % failing_step['sequence'],
                "   target: %s" % failing_step['target'],
                "   command: %s" % failing_step['command'],
                "   value: %s" % failing_step['value'],
                "   error: %s" % failing_step['error']
            ])


    def reportinfo(self):
        return self.fspath, 0, "%s :: %s" % (self.spec['suite'], self.name)


class GIException(Exception):
    """ custom failure reporting """
