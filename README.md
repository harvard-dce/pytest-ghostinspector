# pytest-ghostinspector

[![Build Status](https://travis-ci.org/harvard-dce/pytest-ghostinspector.svg?branch=master)](https://travis-ci.org/harvard-dce/pytest-ghostinspector)

For discovering & executing [Ghost Inspector](https://ghostinspector.com/) tests.


## Features

pytest-ghostinspector is a plugin that leverages the pytest
framework and test runner to execute Ghost Inspector tests
via their REST API. Instead of standard test code, you create
your functional web application tests via the Ghost Inspector
UI and/or test recorder, then specify the suites or individual
tests to execute using a YAML config file or command-line
arguments. The API key and any necessary test variables are
also specified either as command-line arguments or in a
`pytest.ini` file.

## Requirements

* works for python 2.6 - 3.5
* A Ghost Inspector account & api key


## Installation

The usual...

    $ pip install pytest-ghostinspector


## Usage

This plugin adds several command-line arguments to py.test::

    ghostinspector:
      --gi_key=GI_KEY       Set the value for the Ghost Inspector API key
      --gi_start_url=GI_START_URL
                            Override the starting url value for the Ghost
                            Inspector tests
      --gi_suite=GI_SUITE   Id of a Ghost Inspector suite to execute
      --gi_test=GI_TEST     Id of a Ghost Inspector test to execute
      --gi_param=GI_PARAM   Querystring param (repeatable) to include in the API
                            execute request. Example: "--gi_param foo=bar"


### via command line options

Once installed the simplest way to execute your Ghost Inspector tests is via
command-line options to py.test::

    $ py.test --gi_key=hjkl1234 --gi_test=asdf0987

Output should look something like::

    ============================== test session starts =============================
    platform linux2 -- Python 2.7.10, pytest-2.8.3, py-1.4.30, pluggy-0.3.1
    rootdir: /path/to/cwd, inifile:
    plugins: ghostinspector-0.1.0
    collected 1 items

    . .

    ============================ 1 passed in 26.34 seconds =========================


### via YAML test files

If you have a large enough collections of tests or suites you can create a
YAML test file containing the ids and the plugin will collect and
execute them::

    # gi_test_my_tests.yml

    suites:
      - id: abcd1234
      - id: fdsa9876

    tests:
      - id: qwer4567

Then point py.test at the YAML file::

    $ py.test gi_tests/gi_test_my_tests.yml


### pytest.ini 

To avoid having to type common options, like `--gi_key`, include them in a
`pytest.ini` file with `addopts`::

    [pytest]
    ...
    addopts =
        --gi_key=abcd1234
        --gi_param foo=bar
        
### Collection modes

v0.4.0 introduced the `--gi_collect_mode` option for controlling how the plugin
deals with test collection. The options are:

* "all" - specify GI tests via `--gi-test`/`--gi-suite` options, plus standard file system test discovery enabled
* "files" - disables GI API collection via `--gi-test`/`--gi-suite`
* "ids" - disables file system test discovery; only collect tests identified via `--gi-test`/`--gi-suite` 

The `ids` mode can be useful in situations where you only wish to use the plugin
to execute a known set of tests and/or suites, and skip any tests that might be found by searching `cwd`.

By default, if no mode is explicitly passed the inclusion of `--gi-test`/`--gi-suite` will trigger `ids` mode. 

## Development

Contributions are very welcome. Tests can be run with `tox`.

## License

Distributed under the terms of the MIT license, `pytest-ghostinspector` is free and open source software.

## Copyright

2015 President and Fellows of Harvard College

## Hat-tips

This plugin was generated with [Cookiecutter](https://github.com/audreyr/cookiecutter) 
along with @hackebrot's [Cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin) template.

