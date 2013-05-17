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
from wight.worker.runners import FunkLoadBenchRunner
from tests.functional.base import FunkLoadBaseTest

root_path = abspath(join(dirname(__file__), '..', '..'))


class TestCanRunFunkloadBench(FunkLoadBaseTest):
    def test_can_run_funkload(self):
        conf = WightConfig.load(join(root_path, 'bench', 'wight.yml'))
        test = conf.tests[0]
        result = FunkLoadBenchRunner.run(root_path, test, self.base_url, cycles=[10, 20], duration=5)

        expect(result).not_to_be_null()
        expect(result.exit_code).to_equal(0)

        expect(result.text).to_include("SUCCESSFUL")

        expect(result.log).to_be_empty()

        expect(result.xml).not_to_be_null()
        expect(result.result).not_to_be_null()
        expect(result.config).not_to_be_null()
