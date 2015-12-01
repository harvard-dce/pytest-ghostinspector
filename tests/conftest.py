import re
import pytest
from pytest_gi.plugin import API_URL

pytest_plugins = 'pytester'

@pytest.fixture()
def gi_api_suite_tests_re():
    return re.compile(API_URL + 'suites/\w+/tests/')

@pytest.fixture()
def gi_api_test_re():
    return re.compile(API_URL + 'tests/\w+/$')

@pytest.fixture()
def gi_api_test_exec_re():
    return re.compile(API_URL + 'tests/\w+/execute/')



