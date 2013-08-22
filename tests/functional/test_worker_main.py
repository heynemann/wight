#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
import os
from os.path import join
from os import mkdir

from mock import patch
from preggy import expect
from tempfile import mkdtemp

from wight.worker import BenchRunner, WightConfig
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
        runner.run_project_tests(temp_path, str(load_test.uuid), duration=1)

        loaded = LoadTest.objects(uuid=load_test.uuid).first()

        expect(loaded).not_to_be_null()
        expect(loaded.status).to_equal("Finished")

        expect(loaded.results).to_length(1)

        expect(loaded.results[0].log).not_to_be_null()
        expect(loaded.results[0].status).to_equal("Successful")

    @patch.object(BenchRunner, '_build_test_config')
    def test_can_run_project_with_two_test(self, build_mock):
        simple_test_content = """
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase


class SimpleTestTest(FunkLoadTestCase):
    def setUp(self):
        self.server_url = '%s/healthcheck' % (self.conf_get('main', 'url').rstrip('/'),)

    def test_simple(self):
        self.get(self.server_url, description='Get url')

if __name__ == '__main__':
    unittest.main()

"""

        healthcheck_content = """
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase


class HealthCheckTest(FunkLoadTestCase):
    def setUp(self):
        self.server_url = '%s/healthcheck' % (self.conf_get('main', 'url').rstrip('/'),)

    def test_healthcheck(self):
        self.get(self.server_url, description='Get url')

if __name__ == '__main__':
    unittest.main()

"""
        cfg_text = """
tests:
  -
    module: test_healthcheck.py
    class: HealthCheckTest
    test: test_healthcheck
  -
    module: test_simple.py
    class: SimpleTestTest
    test: test_simple
"""

        build_mock.return_value = WightConfig(cfg_text)

        team = TeamFactory.create()
        TeamFactory.add_projects(team, 1)
        user = team.owner
        project = team.projects[0]
        load_test = LoadTestFactory.add_to_project(1, user=user, team=team, project=project, base_url=self.base_url, simple=True)

        temp_path = mkdtemp()

        mkdir(join(temp_path, "bench"))
        init_file = open(join(temp_path, "bench/__init__.py"), "w")
        init_file.close()
        wight_file = open(join(temp_path, "bench/wight.yml"), "w")
        wight_file.write(cfg_text)
        wight_file.close()

        simple_file = open(join(temp_path, "bench/test_simple.py"), "w")
        simple_file.write(simple_test_content)
        simple_file.close()

        healthcheck_file = open(join(temp_path, "bench/test_healthcheck.py"), "w")
        healthcheck_file.write(healthcheck_content)
        healthcheck_file.close()

        runner = BenchRunner()
        runner.run_project_tests(temp_path, str(load_test.uuid), duration=1)

        loaded = LoadTest.objects(uuid=load_test.uuid).first()
        expect(loaded).not_to_be_null()
        expect(loaded.status).to_equal("Finished")

        expect(loaded.results).to_length(2)

        expect(loaded.results[0].log).not_to_be_null()
        expect(loaded.results[0].status).to_equal("Successful")
        expect(loaded.results[0].config.module).to_equal("test_healthcheck")

        expect(loaded.results[1].log).not_to_be_null()
        expect(loaded.results[1].status).to_equal("Successful")
        expect(loaded.results[1].config.module).to_equal("test_simple")

    def test_can_run_simple_project(self):
        temp_path = mkdtemp()
        team = TeamFactory.create()
        TeamFactory.add_projects(team, 1)
        user = team.owner
        project = team.projects[0]
        load_test = LoadTestFactory.add_to_project(1, user=user, team=team, project=project, base_url="%s/healthcheck" % self.base_url, simple=True)

        runner = BenchRunner()
        runner.run_project_tests(temp_path, str(load_test.uuid), duration=1)

        loaded = LoadTest.objects(uuid=load_test.uuid).first()

        expect(loaded).not_to_be_null()
        expect(loaded.status).to_equal("Finished")

        expect(loaded.results).to_length(1)

        expect(loaded.results[0].log).not_to_be_null()
        expect(loaded.results[0].status).to_equal("Successful")
        expect(loaded.results[0].config.module).to_equal("test_simple")
        expect(loaded.results[0].config.class_name).to_equal("SimpleTestTest")
        expect(loaded.results[0].config.test_name).to_equal("test_simple")

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
