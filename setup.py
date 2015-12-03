#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()

version_file = read('pytest_gi/__init__.py')
version = re.search(
    r"^__version__ = ['\"]([^'\"]*)['\"]",
    version_file,
    re.M).group(1)

setup(
    name='pytest-ghostinspector',
    version=version,
    author='Jay Luker',
    author_email='jay_luker@harvard.edu',
    license='MIT',
    url='https://github.com/harvard-dce/pytest-ghostinspector',
    description='For finding/executing Ghost Inspector tests',
    long_description=read('README.md'),
    py_modules=['pytest_gi.plugin'],
    install_requires=['pytest>=2.8.1', 'requests>=2.7', 'pyyaml'],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
        'Topic :: Software Development :: Testing'
    ],
    keywords=['pytest', 'py.test', 'ghostinspector'],
    entry_points={
        'pytest11': [
            'ghostinspector = pytest_gi.plugin',
        ],
    },
)
