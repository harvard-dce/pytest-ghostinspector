# -*- coding: utf-8 -*-

import pytest
from pytest_httpretty import stub_get

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
def test_cmdline_collect_suite(testdir, suite_resp, gi_api_suite_tests_re):

    stub_get(
        gi_api_suite_tests_re,
        body=suite_resp,
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
def test_cmdline_collect_test(testdir, test_resp, gi_api_test_re):

    stub_get(
        gi_api_test_re,
        body=test_resp,
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
def test_cmdline_exec_test(testdir, test_resp, gi_api_test_re, gi_api_test_exec_re):

    def req_callback(request, uri, headers):
        return (
            200,
            headers,
            '{ "data": { "passing": true } }'
        )

    stub_get(
        gi_api_test_re,
        content_type="application/json",
        body=test_resp
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

def test_collect_mode_files(testdir):
    testdir.makepyfile('def test_fail(): assert 0')

    # this should result in a GI API error that the gi test was not found;
    # meant to confirm that the --gi_test option is triggering an attempt to
    # collect via the GI API
    result = testdir.runpytest(
        '--collect-only',
        '--gi_key=foo',
        '--gi_test=xyz789'
    )
    result.stdout.fnmatch_lines([
        '*Test not found*'
    ])

    # this will pass because collect mode "files" skips collection via
    # the GI API
    result = testdir.runpytest(
        '--collect-only',
        '--gi_key=foo',
        '--gi_test=xyz789',
        '--gi_collect_mode=files'
    )
    result.stdout.fnmatch_lines([
        'collected 1 items',
        '*test_fail*'
    ])

@pytest.mark.httpretty
def test_collect_mode_all(testdir, test_resp, gi_api_test_re):
    testdir.makepyfile('def test_fail(): assert 0')

    stub_get(
        gi_api_test_re,
        body=test_resp,
        content_type="application/json"
    )

    result = testdir.runpytest(
        '--collect-only',
        '--gi_key=foo',
        '--gi_test=xyz789',
        '--gi_collect_mode=all'
    )

    result.stdout.fnmatch_lines([
        u'collected 2 items',
        u"*test_fail*",
        u"*GITestItem*'test xyz789'*"
    ])

@pytest.mark.httpretty
def test_collect_mode_ids(testdir, test_resp, gi_api_test_re):
    testdir.makepyfile('def test_fail(): assert 0')

    stub_get(
        gi_api_test_re,
        body=test_resp,
        content_type="application/json"
    )

    # use of --gi_test/--gi_suite opts auto triggers "ids" collect mode
    result = testdir.runpytest(
        '--collect-only',
        '--gi_key=foo',
        '--gi_test=xyz789',
    )

    result.stdout.fnmatch_lines([
        u'collected 1 items',
        u"*GITestItem*'test xyz789'*"
    ])
