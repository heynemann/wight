#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.worker.config import WightConfig
from tests.functional.base import TestCase


class TestCanCloneRepository(TestCase):
    def test_can_parse_configuration(self):
        cfg_text = """
tests:
  -
    title: HealthCheck Test
    module: healthcheck.py
    class: HealthCheckTest
    test: test_healthcheck
"""

        cfg = WightConfig(cfg_text)

        expect(cfg).not_to_be_null()
        expect(cfg.tests).to_length(1)

        expect(cfg.tests[0].title).to_equal("HealthCheck Test")
        expect(cfg.tests[0].module).to_equal("healthcheck.py")
        expect(cfg.tests[0].class_name).to_equal("HealthCheckTest")
        expect(cfg.tests[0].test_name).to_equal("test_healthcheck")
