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
from tests.factories import LoadTestFactory, TeamFactory

root_path = abspath(join(dirname(__file__), '..', '..'))


#class TestWorkerMain(FunkLoadBaseTest):
    #def test_can_run_project(self):
        #team = TeamFactory.create()
        #TeamFactory.add_projects(team, 1)
        #user = team.owner
        #project = team.projects[0]
        #project.repository = "git://github.com/heynemann/wight.git"
        #load_test = LoadTestFactory.add_to_project(1, user=user, team=team, project=project)

        #conf = WightConfig.load(join(root_path, 'bench', 'wight.yml'))
        #test = conf.tests[0]
        #result = FunkLoadBenchRunner.run(root_path, test, self.base_url, cycles=[10, 20], duration=5)

        #expect(result).not_to_be_null()
        #expect(result.exit_code).to_equal(0)

        #expect(result.text).to_include("SUCCESSFUL")

        #expect(result.log).to_be_empty()

        #expect(result.xml).not_to_be_null()
        #expect(result.result).not_to_be_null()
        #expect(result.config).not_to_be_null()

        #load_test.add_result(result.config, result.result)

        #expect(load_test.results).to_length(1)
