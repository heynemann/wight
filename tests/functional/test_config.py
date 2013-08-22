#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import abspath, join, dirname

from preggy import expect

from wight.worker.config import WightConfig
from tests.functional.base import TestCase

root_path = abspath(join(dirname(__file__), '..'))


class TestCanCloneRepository(TestCase):
    def test_can_parse_configuration(self):
        cfg_text = """
tests:
  -
    module: healthcheck.py
    class: HealthCheckTest
    test: test_healthcheck
"""

        cfg = WightConfig(cfg_text)

        expect(cfg).not_to_be_null()
        expect(cfg.tests).to_length(1)

        expect(cfg.tests[0].module).to_equal("healthcheck.py")
        expect(cfg.tests[0].class_name).to_equal("HealthCheckTest")
        expect(cfg.tests[0].test_name).to_equal("test_healthcheck")

    def test_can_parse_configuration_with_more_tests(self):
        cfg_text = """
tests:
  -
    module: healthcheck.py
    class: HealthCheckTest
    test: test_healthcheck
  -
    module: healthcheck2.py
    class: HealthCheckTest2
    test: test_healthcheck2
"""

        cfg = WightConfig(cfg_text)

        expect(cfg).not_to_be_null()
        expect(cfg.tests).to_length(2)

        expect(cfg.tests[1].module).to_equal("healthcheck2.py")
        expect(cfg.tests[1].class_name).to_equal("HealthCheckTest2")
        expect(cfg.tests[1].test_name).to_equal("test_healthcheck2")

    def test_can_parse_configuration_with_deps(self):
        cfg_text = """
tests:
  -
    module: healthcheck.py
    class: HealthCheckTest
    test: test_healthcheck
    deps:
      - request
      - six
"""

        cfg = WightConfig(cfg_text)

        expect(cfg).not_to_be_null()
        expect(cfg.tests).to_length(1)
        expect(cfg.tests[0].deps).to_be_like(["request", "six"])

    def test_can_load_files(self):
        cfg = WightConfig.load(join(root_path, 'wight.yml'))

        expect(cfg).not_to_be_null()
        expect(cfg.tests).to_length(1)

        expect(cfg.tests[0].module).to_equal("healthcheck.py")
        expect(cfg.tests[0].class_name).to_equal("HealthCheckTest")
        expect(cfg.tests[0].test_name).to_equal("test_healthcheck")

    def test_loading_a_file_that_does_not_exist_returns_none(self):
        cfg = WightConfig.load('/invalid/path')
        expect(cfg).to_be_null()
