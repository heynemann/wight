#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
import os

from mock import patch
from preggy import expect
from tempfile import mkdtemp

from wight.worker import BenchRunner
from wight.models import LoadTest
from tests.functional.base import FunkLoadBaseTest
from tests.factories import LoadTestFactory, TeamFactory


class TestWorkerMain(FunkLoadBaseTest):

    def test_can_run_project(self):
        temp_path = mkdtemp()

        team = TeamFactory.create()
        TeamFactory.add_projects(team, 1)
        user = team.owner
        project = team.projects[0]
        project.repository = "git://github.com/heynemann/wight.git"
        load_test = LoadTestFactory.add_to_project(1, user=user, team=team, project=project, base_url=self.base_url)

        runner = BenchRunner()
        runner.run_project_tests(temp_path, str(load_test.uuid), cycles=[1, 2], duration=1)

        loaded = LoadTest.objects(uuid=load_test.uuid).first()

        expect(loaded).not_to_be_null()
        expect(loaded.status).to_equal("Finished")

        expect(loaded.results).to_length(1)

        expect(loaded.results[0].log).not_to_be_null()
        expect(loaded.results[0].status).to_equal("Successful")

    @patch.object(BenchRunner, '_clone_repository')
    def test_fail_if_yaml_not_exists(self, clone_repo_mock):
        clone_repo_mock.return_value = None
        temp_path = mkdtemp()
        os.mkdir(os.path.join(temp_path, "bench"))
        load_test = LoadTestFactory.add_to_project(1, base_url=self.base_url)

        runner = BenchRunner()
        runner.run_project_tests(temp_path, str(load_test.uuid), cycles=[1, 2], duration=1)

        loaded = LoadTest.objects(uuid=load_test.uuid).first()

        expect(loaded).not_to_be_null()
        expect(loaded.status).to_equal("Failed")
        expect(loaded.error).to_equal("The wight.yml file was not found in project repository bench folder.")
