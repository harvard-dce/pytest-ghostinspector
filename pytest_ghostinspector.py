# -*- coding: utf-8 -*-

import pytest
import requests
import itertools

GI_API_URL = 'https://api.ghostinspector.com/v1/'

def pytest_addoption(parser):
    group = parser.getgroup('ghostinspector')
    group.addoption(
        '--gi_key',
        action='store',
        dest='gi_key',
        help='Set the value for the Ghost Inspector API key'
    )

    parser.addini('gi_key', 'Dummy pytest.ini setting')


@pytest.fixture
def gi_key(request):
    return request.config.option.gi_key

def pytest_configure(config):
    """Configuration hook to verify we got the necessary options"""
    if config.option.gi_key is None:
        raise pytest.UsageError("Missing --gi_key option")

def pytest_collect_file(path, parent):
    """Collection hook for ghost inspector tests

    This looks for yaml files containing configuration info for executing
    http://ghostinspector.com tests via the API
    """
    if str(path.basename.startswith('gi_test_')) and path.ext == '.yml':
        return GICollector(path, parent=parent)

class GICollector(pytest.File):

    def __init__(self, *args, **kwargs):
        super(GICollector, self).__init__(*args, **kwargs)
        self.api_key = self.config.option.gi_key

    def collect(self):
        import yaml
        raw = yaml.safe_load(self.fspath.open())
        test_iters = []
        for suite in raw.get('suites', []):
            for test_item in self._collect_suite(suite):
                yield test_item
        for test in raw.get('tests', []):
            yield self._collect_test(test)

    def _collect_suite(self, suite):
        url = GI_API_URL + 'suites/{}/tests/'.format(suite['id'])
        test_list = self._request(url)
        for test in test_list:
            spec = {
                'id': test['_id'],
                'suite': test['suite']['name']
            }
            yield GITestItem(test['name'], self, spec)

    def _collect_test(self, test):
        url = GI_API_URL + 'tests/{}/'.format(test['id'])
        test_data = self._request(url)
        spec = {
            'id': test_data['_id'],
            'suite': test_data['suite']['name']
        }
        return GITestItem(test_data['name'], self, spec)

    def _request(self, url, params=None):
        if params is None:
            params = {}
        params['apiKey'] = self.api_key
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()['data']

class GITestItem(pytest.Item):

    def __init__(self, name, parent, spec):
        super(GITestItem, self).__init__(name, parent)
        self.spec = spec


