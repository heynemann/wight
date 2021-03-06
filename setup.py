#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from setuptools import setup, find_packages
from wight import __version__, FUNKLOAD_GIT

tests_require = [
    'nose',
    'coverage',
    'yanc',
    'preggy==0.5.11',
    'mock',
    'tox',
    'ipdb',
    'sh',
    'factory_boy',
    'coveralls',
    'pexpect-u',
    'pygit2'
]

setup(
    name='wight',
    version=__version__,
    description='wight is a load testing scheduling and tracking tool.',
    long_description='''
wight is a load testing scheduling and tracking tool.
''',
    keywords='test testing load performance profile profiling',
    author='Bernardo Heynemann',
    author_email='heynemann@gmail.com',
    url='http://github.com/heynemann/wight/',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing'
    ],
    packages=find_packages(),
    include_package_data = True,
    dependency_links = ['%s#egg=funkload-1.17.0' % FUNKLOAD_GIT],
    install_requires=[
        'argparse',
        'cement',
        'derpconf==0.4.7',
        'tornado',
        'redis',
        'mongoengine',
        'requests',
        'prettytable',
        'colorama',
        'pyyaml',
        'funkload>=1.17.0',
        'pyres',
        'paramiko==1.10.1',
        'virtualenv==1.9.1',
        'sh',
        'python-dateutil',
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
            'wight=wight.cli:main',
            'wight-api=wight.api.server:main',
            'wight-web=wight.web.server:main',
            'wight-worker=wight.worker:main'
        ],
    },
)
