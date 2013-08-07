#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from tempfile import NamedTemporaryFile
from preggy import expect
from tests.unit.base import WorkerTestCase

import mock
import sys

from wight.worker.bench_configuration import BenchConfiguration


class TestBenchConfiguration(WorkerTestCase):

    @mock.patch('wight.worker.bench_configuration.sys', executable='/bin/python')
    def test_generate_conf_with_workers_password(self, executable_mock):
        bench = BenchConfiguration('test', 'test', 'test', workers = [
                    {
                        "host": "ma-amazing-host",
                        "user": "user",
                        "password": "password",
                    },
                ])
        with NamedTemporaryFile() as temp_file:
            bench.save(temp_file.name)
            expect(temp_file.read()).to_be_like('''
[main]
title=test
description=test

[bench]
duration=10
startup_delay = 0.01
cycle_time = 1
sleep_time = 0.01
sleep_time_min = 0.00
sleep_time_max = 0.50

[test]
description=test
[distribute]
log_path =
python_bin = /bin/python
funkload_location=https://github.com/nuxeo/FunkLoad/archive/master.zip

[workers]
hosts = worker_0
[worker_0]
host = ma-amazing-host
username = user
password = password
''')

    @mock.patch('wight.worker.bench_configuration.sys', executable='/bin/python')
    def test_generate_conf_with_workers_key(self, executable_mock):
        bench = BenchConfiguration('test', 'test', 'test', workers=[
            {
                "host": "ma-amazing-host",
                "user": "user",
                "ssh_key": "/path/my.pem",
            },
        ])

        with NamedTemporaryFile() as temp_file:
            bench.save(temp_file.name)
            expect(temp_file.read()).to_be_like('''
[main]
title=test
description=test

[bench]
duration=10
startup_delay = 0.01
cycle_time = 1
sleep_time = 0.01
sleep_time_min = 0.00
sleep_time_max = 0.50

[test]
description=test
[distribute]
log_path =
python_bin = /bin/python
funkload_location=https://github.com/nuxeo/FunkLoad/archive/master.zip

[workers]
hosts = worker_0
[worker_0]
host = ma-amazing-host
username = user
ssh_key = /path/my.pem
''')
