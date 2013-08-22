#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import re
from os.path import abspath, join, dirname

from preggy import expect

from wight.worker.config import WightConfig
from wight.worker.runners import FunkLoadTestRunner
from tests.functional.base import FunkLoadBaseTest

root_path = abspath(join(dirname(__file__), '..', '..'))


class TestCanRunFunkloadTest(FunkLoadBaseTest):
    def test_can_run_funkload(self):
        conf = WightConfig.load(join(root_path, 'bench', 'wight.yml'))
        test = conf.tests[0]
        result = FunkLoadTestRunner.run(root_path, test, self.base_url)

        expect(result).not_to_be_null()
        expect(result.exit_code).to_equal(0)

        text = re.sub(r"\d[.]\d{3}s", "", result.text)

        expect(text).to_be_like("""
            test_healthcheck: [ftest] sleep_time_min not found
            test_healthcheck: [ftest] sleep_time_max not found
            test_healthcheck: [ftest] log_path not found
            test_healthcheck: [ftest] result_path not found
            .
            ----------------------------------------------------------------------
            Ran 1 test in

            OK
        """)

        log = re.sub("\d*\-\d*\-\d*\s\d*[:]\d*[:]\d*[,]\d*\s", "", result.log)
        log = re.sub(r"\d[.]\d{3}s", "", log)

        expect(log).to_be_like("""
        INFO test_healthcheck: [test_healthcheck] description not found
        DEBUG test_healthcheck: Starting -----------------------------------
        DEBUG test_healthcheck: GET: http://localhost:2368/HealthCheck
            Page 1: Get url ...
        DEBUG test_healthcheck:  Done in
        """)

    def test_can_report_failure(self):
        test_path = join(root_path, 'tests', 'functional')
        conf = WightConfig.load(join(test_path, 'failures.yml'))
        test = conf.tests[0]
        result = FunkLoadTestRunner.run(test_path, test, self.base_url)

        expect(result).not_to_be_null()
        expect(result.exit_code).to_equal(1)
        expect(result.text).to_include("ImportError: No module named fail")
