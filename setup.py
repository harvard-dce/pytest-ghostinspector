#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-ghostinspector',
    version='0.1.0',
    author='Jay Luker',
    author_email='lbjay@reallywow.com',
    maintainer='Jay Luker',
    maintainer_email='lbjay@reallywow.com',
    license='MIT',
    url='https://github.com/lbjay/pytest-ghostinspector',
    description='For finding/executing Ghost Inspector tests',
    long_description=read('README.rst'),
    py_modules=['pytest_ghostinspector'],
    install_requires=['pytest>=2.8.1', 'requests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'ghostinspector = pytest_ghostinspector',
        ],
    },
)
