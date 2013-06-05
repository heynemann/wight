#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import abspath, join, dirname

from preggy import expect

from wight.models import LoadTest
from wight.worker.config import WightConfig
from wight.worker.runners import FunkLoadBenchRunner
from tests.functional.base import FunkLoadBaseTest
from tests.factories import LoadTestFactory, TeamFactory

root_path = abspath(join(dirname(__file__), '..', '..'))


class TestCanRunFunkloadBench(FunkLoadBaseTest):
    def test_can_run_funkload(self):
        team = TeamFactory.create()
        TeamFactory.add_projects(team, 1)
        user = team.owner
        project = team.projects[0]
        load_test = LoadTestFactory.add_to_project(1, user=user, team=team, project=project)

        conf = WightConfig.load(join(root_path, 'bench', 'wight.yml'))
        test = conf.tests[0]
        fl_result = FunkLoadBenchRunner.run(root_path, test, self.base_url, cycles=[10, 20], duration=5)

        expect(fl_result).not_to_be_null()
        expect(fl_result.exit_code).to_equal(0)

        expect(fl_result.text).to_include("SUCCESSFUL")

        expect(fl_result.log).to_be_empty()

        expect(fl_result.result).not_to_be_null()
        expect(fl_result.config).not_to_be_null()

        result = LoadTest.get_data_from_funkload_results(fl_result.config, fl_result.result)

        load_test.add_result(result, fl_result.text)

        expect(load_test.results).to_length(1)
