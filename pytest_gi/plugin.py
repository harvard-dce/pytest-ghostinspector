# -*- coding: utf-8 -*-

import yaml
import pytest
import shutil
import requests
import tempfile
from os import getenv as env
from contextlib import contextmanager

API_URL = env('GI_API_URL', 'https://api.ghostinspector.com/v1/')
API_KEY = env('GI_API_KEY')
START_URL = env('GI_START_URL')


# Command-line Options

def pytest_addoption(parser):
    group = parser.getgroup('ghostinspector')
    group.addoption(
        '--gi_key',
        action='store',
        dest='gi_key',
        default=API_KEY,
        help='Set the value for the Ghost Inspector API key'
    )
    group.addoption(
        '--gi_start_url',
        action='store',
        dest='gi_start_url',
        default=START_URL,
        help='Override the starting url value for the Ghost Inspector tests'
    )
    group.addoption(
        '--gi_suite',
        action='append',
        dest='gi_suite',
        default=[],
        help='Id of a Ghost Inspector suite to execute'
    )
    group.addoption(
        '--gi_test',
        action='append',
        dest='gi_test',
        default=[],
        help='Id of a Ghost Inspector test to execute'
    )

    group.addoption(
        '--gi_param',
        action='append',
        dest='gi_param',
        default=[],
        help=(
            'Querystring param (repeatable) to include '
            'in the API execute request. Example: "--gi_param foo=bar"'
        )
    )

    group.addoption(
        '--gi_collect_mode',
        action='store',
        dest='gi_collect_mode',
        type=str,
        choices=['files', 'ids', 'all'],
        help=('specifiy "files", "ids" or "all" to control how the plugin '
              'manages test collection')
    )

def pytest_configure(config):
    # only do logic if mode is not explicitly set
    if config.option.gi_collect_mode is None:
        if config.option.gi_test or config.option.gi_suite:
            # this will disable file/directory test discovery
            config.option.gi_collect_mode = "ids"


@pytest.hookimpl(hookwrapper=True)
def pytest_collection(session):
    """
    Allow execution of suites/tests specified via cmdline opts. Creates temp
    yaml files for the discover/collection process.
    """

    @contextmanager
    def _make_tmp_dir():
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir)

    def _make_tmp_yaml(tmpdir, data):
        tf = tempfile.NamedTemporaryFile('wt',
                                         prefix='gi_test_',
                                         suffix='.yml',
                                         dir=tmpdir,
                                         delete=False)
        yaml.safe_dump(data, tf)
        tf.close()
        return tf.name

    if not session.config.option.gi_suite \
            and not session.config.option.gi_test:
        yield
    elif session.config.option.gi_collect_mode == "files":
        yield
    else:
        with _make_tmp_dir() as tmpdir:
            tmp_files = []
            for id in session.config.option.gi_suite:
                test_yaml = {'suites': [{'id': id}]}
                tmp_files.append(_make_tmp_yaml(tmpdir, test_yaml))
            for id in session.config.option.gi_test:
                test_yaml = {'tests': [{'id': id}]}
                tmp_files.append(_make_tmp_yaml(tmpdir, test_yaml))
            session.config.args += tmp_files
            yield


def pytest_collect_file(path, parent):
    """Collection hook for ghost inspector tests

    This looks for yaml files containing configuration info for executing
    http://ghostinspector.com tests via the API
    """
    if path.basename.startswith('gi_test_') and path.ext == '.yml':
        if parent.config.option.gi_key is None:
            raise pytest.UsageError("Missing --gi_key option")
        return GIYamlCollector(path, parent=parent)


def pytest_ignore_collect(path, config):
    """
    Disable file/directory collection when --gi-test/--gi-suite options are
    provided
    """
    if config.option.gi_collect_mode == "ids":
        return True


class GIAPIMixin(object):

    def _api_request(self, url, params=None):
        if params is None:
            params = {}
        params['apiKey'] = self.gi_key
        if self.config.option.gi_start_url is not None:
            params['startUrl'] = self.config.option.gi_start_url
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            resp_data = resp.json()
            if 'errorType' in resp_data:
                raise self.CollectError(
                    "Ghost Inspector API returned error: %s" %
                    resp_data['message'])
            return resp_data['data']
        except Exception as e:
            raise self.CollectError(str(e))


class GIYamlCollector(pytest.File, GIAPIMixin):
    """Collect and generate pytest test items based on yaml config"""

    def __init__(self, *args, **kwargs):
        super(GIYamlCollector, self).__init__(*args, **kwargs)
        self.gi_key = self.config.option.gi_key

    def collect(self):
        raw = yaml.safe_load(self.fspath.open())

        for suite in raw.get('suites', []):
            for test_item in self._collect_suite(suite):
                yield test_item

        for test in raw.get('tests', []):
            yield self._collect_test(test)

    def _collect_suite(self, suite):
        url = API_URL + ('suites/%s/tests/' % suite['id'])
        test_list = self._api_request(url)
        for test_config in test_list:
            yield self._create_test_item(test_config)

    def _collect_test(self, test):
        url = API_URL + ('tests/%s/' % test['id'])
        test_config = self._api_request(url)
        return self._create_test_item(test_config)

    def _create_test_item(self, test_config):

        params = dict(x.split('=') for x in self.config.option.gi_param)
        spec = {
            'id': test_config['_id'],
            'suite': test_config['suite']['name'],
            'params': params
        }
        return GITestItem(test_config['name'], self, spec)


class GITestItem(pytest.Item, GIAPIMixin):

    def __init__(self, name, parent, spec):
        super(GITestItem, self).__init__(name, parent)
        self.gi_key = self.config.option.gi_key
        self.spec = spec

    def runtest(self):
        url = API_URL + ('tests/%s/execute/' % self.spec['id'])
        result = self._api_request(url, self.spec['params'])
        if not result['passing']:
            raise GIException(self, result)

    def repr_failure(self, excinfo):
        """ format failure info from GI API response """
        if isinstance(excinfo.value, GIException):
            resp_data = excinfo.value.args[1]
            failing_step = next(
                step for step in resp_data['steps'] if not step['passing']
            )

            if 'error' in resp_data:
                error_msg = resp_data['error']['details']
            else:
                error_msg = ''

            result_url_base = 'https://app.ghostinspector.com/results'
            return "\n".join([
                "Ghost Inspector test failed",
                "   name: %s" % resp_data['test']['name'],
                "   start url: %s" % resp_data['startUrl'],
                "   end url: %s" % resp_data['endUrl'],
                "   result url: %s/%s" % (result_url_base, resp_data['_id']),
                "   sequence: %d" % failing_step['sequence'],
                "   target: %s" % failing_step['target'],
                "   command: %s" % failing_step['command'],
                "   value: %s" % failing_step['value'],
                "   error: %s" % error_msg,
                "   step error: %s" % failing_step.get('error', '')
            ])

    def reportinfo(self):
        return self.fspath, 0, "%s :: %s" % (self.spec['suite'], self.name)


class GIException(Exception):
    """ custom failure reporting """
