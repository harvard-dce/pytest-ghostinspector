# -*- coding: utf-8 -*-

import pytest
from pytest_httpretty import stub_get

SUITE_RESP = '''
{
    "data": [
        { "_id": 1, "name": "test 1", "suite": { "name": "ABC Suite" } },
        { "_id": 2, "name": "test 2", "suite": { "name": "ABC Suite" } }
    ]
}
'''

TEST_RESP = '''
{
    "data": {
        "_id": "xyz789",
        "name": "test xyz789",
        "suite": { "name": "ABC Suite" }
    }
}
'''

def test_help_message(testdir):

    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        u'ghostinspector:'
    ])

def test_key_option(testdir):

    config = testdir.parseconfig(
        '--gi_key=foo',
    )
    assert config.option.gi_key == 'foo'

def test_start_url_option(testdir):

    config = testdir.parseconfig(
        '--gi_start_url=bar',
    )
    assert config.option.gi_start_url == 'bar'

def test_suite_option(testdir):

    config = testdir.parseconfig()
    assert config.option.gi_suite == []

    config = testdir.parseconfig(
        '--gi_suite=abc123',
        '--gi_suite=def456',
    )
    assert config.option.gi_suite == ['abc123', 'def456']

def test_test_option(testdir):

    config = testdir.parseconfig()
    assert config.option.gi_test == []

    config = testdir.parseconfig(
        '--gi_test=xyz789'
    )
    assert config.option.gi_test == ['xyz789']

def test_param_option(testdir):

    config = testdir.parseconfig()
    assert config.option.gi_param == []

    config = testdir.parseconfig(
        '--gi_param=foo=bar',
        '--gi_param=baz=blerg'
    )
    assert config.option.gi_param == ['foo=bar', 'baz=blerg']

@pytest.mark.httpretty
def test_cmdline_empty_suite(testdir, gi_api_suite_tests_re):

    stub_get(
        gi_api_suite_tests_re,
        body='{ "data": [] }',
        content_type='application/json'
    )

    result = testdir.runpytest(
        '--gi_key=foo',
        '--gi_suite=abc123'
    )
    result.stdout.fnmatch_lines([
        u'collected 0 items'
    ])

@pytest.mark.httpretty
def test_cmdline_404_suite(testdir, gi_api_suite_tests_re):

    stub_get(
        gi_api_suite_tests_re,
        body='{ "errorType": "VALIDATION_ERROR", "message": "Suite not found" }',
        content_type='application/json'
    )

    result = testdir.runpytest(
        '--gi_key=foo',
        '--gi_suite=abc123'
    )

    result.stdout.fnmatch_lines([
       u'Ghost Inspector API returned error: Suite not found'
    ])

@pytest.mark.httpretty
def test_cmdline_collect_suite(testdir, gi_api_suite_tests_re):

    stub_get(
        gi_api_suite_tests_re,
        body=SUITE_RESP,
        content_type="application/json"
    )

    result = testdir.runpytest(
        '--collect-only',
        '--gi_key=foo',
        '--gi_suite=abc123'
    )

    result.stdout.fnmatch_lines([
        u'collected 2 items',
        u"*GITestItem*'test 1'*",
        u"*GITestItem*'test 2'*",
    ])

@pytest.mark.httpretty
def test_cmdline_collect_test(testdir, gi_api_test_re):

    stub_get(
        gi_api_test_re,
        body=TEST_RESP,
        content_type="application/json"
    )

    result = testdir.runpytest(
        '--collect-only',
        '--gi_key=foo',
        '--gi_test=xyz789'
    )

    result.stdout.fnmatch_lines([
        u'collected 1 items',
        u"*GITestItem*'test xyz789'*",
    ])

@pytest.mark.httpretty
def test_cmdline_exec_test(testdir, gi_api_test_re, gi_api_test_exec_re):

    def req_callback(request, uri, headers):
        return (
            200,
            headers,
            '{ "data": { "passing": true } }'
        )

    stub_get(
        gi_api_test_re,
        content_type="application/json",
        body=TEST_RESP
    )
    stub_get(
        gi_api_test_exec_re,
        content_type="application/json",
        body=req_callback
    )

    result = testdir.runpytest(
        '--gi_key=foo',
        '--gi_test=xyz789'
    )

    result.stdout.fnmatch_lines([
        u'collected 1 items',
        u"*1 passed*",
    ])
