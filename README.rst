pytest-ghostinspector
===================================

.. image:: https://travis-ci.org/harvard-dce/pytest-ghostinspector.svg?branch=master
    :target: https://travis-ci.org/harvard-dce/pytest-ghostinspector
    :alt: See Build Status on Travis CI

For discovering & executing Ghost Inspector tests


Features
--------

pytest-ghostinspector is a plugin that leverages the pytest
framework and test runner to execute Ghost Inspector tests
via the REST API. Instead of standard test code, you create
your functional web application tests via the Ghost Inspector
UI and/or test recorder, then specify the suites or individual
tests to execute using a YAML config file or command-line
arguments. The API key and any necessary test variables are
also specified either as command-line arguments or in a
`pytest.ini` file.

Requirements
------------

* python >= 2.7


Installation
------------

You can install "pytest-ghostinspector" via `pip`_ from `PyPI`_::

    $ pip install pytest-ghostinspector


Usage
-----

* TODO

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-ghostinspector" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/lbjay/pytest-ghostinspector/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.org/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi

----

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.

Copyright
---------
2015 President and Fellows of Harvard College
