#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import abspath, join, dirname
from tempfile import mkdtemp

from preggy import expect

from wight.worker.bench_configuration import BenchConfiguration
from tests.functional.base import TestCase


class TestBenchConfiguration(TestCase):
    def test_can_create_bench_config(self):
        tst = BenchConfiguration(
            test_name="test_name",
            title="test title",
            description="test description",
            startup_delay=0.01,
            cycle_time=1,
            sleep_time=0.01,
            sleep_time_min=0,
            sleep_time_max=0.5
        )

        expect(tst).not_to_be_null()

        expect(tst.test_name).to_equal("test_name")
        expect(tst.title).to_equal("test title")
        expect(tst.description).to_equal("test description")

        expect(tst.startup_delay).to_equal(0.01)
        expect(tst.cycle_time).to_equal(1)
        expect(tst.sleep_time).to_equal(0.01)
        expect(tst.sleep_time_min).to_equal(0)
        expect(tst.sleep_time_max).to_equal(0.5)

    def test_can_write_to_file(self):
        tst = BenchConfiguration(
            test_name="test_name",
            title="test title",
            description="test description",
            duration=30,
            startup_delay=0.01,
            cycle_time=1,
            sleep_time=0.01,
            sleep_time_min=0,
            sleep_time_max=0.5
        )

        temp_path = mkdtemp()
        conf_path = join(temp_path, 'test.conf')
        tst.save(conf_path)

        with open(conf_path) as conf_file:
            config = conf_file.read()

            expect(config).to_be_like("""
            [main]
            title=test title
            description=test description

            [bench]
            duration = 30
            startup_delay = 0.01
            cycle_time = 1
            sleep_time = 0.01
            sleep_time_min = 0.00
            sleep_time_max = 0.50

            [test_name]
            description=test description
            """)
