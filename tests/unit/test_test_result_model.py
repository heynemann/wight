#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys
from time import sleep
from uuid import uuid4
from mongoengine.errors import DoesNotExist

from preggy import expect

from wight.models import LoadTest
from tests.unit.base import ModelTestCase
from tests.factories import TeamFactory, UserFactory, LoadTestFactory, TestResultFactory, TestConfigurationFactory


class TestTestResultModel(ModelTestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 2)
        self.project = self.team.projects[0]
        self.load_test = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project, status="Finished")

    def test_can_get_load_test_by_test_result_uuid(self):
        self.load_test.results.append(TestResultFactory.build())
        self.load_test.save()
        result = self.load_test.results[0]
        load_test, test_result = LoadTest.get_test_result(str(result.uuid))
        expect(str(test_result.uuid)).to_equal(str(result.uuid))
        expect(str(load_test.uuid)).to_equal(str(self.load_test.uuid))

    def test_should_raise_not_found_if_no_load_test_found(self):
        try:
            LoadTest.get_test_result(uuid4())
            assert False, "Should have raise NotFound in mongo"
        except DoesNotExist:
            assert True

    def test_get_last_result_for_diff(self):
        config = TestConfigurationFactory.build()
        self.load_test.results.append(TestResultFactory.build(config=config))
        self.load_test.results.append(TestResultFactory.build())
        self.load_test.save()
        load_test2 = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project, status="Finished")
        load_test2.results.append(TestResultFactory.build())
        load_test2.results.append(TestResultFactory.build(config=config))
        load_test2.save()

        result1 = self.load_test.results[0]
        result2 = load_test2.results[1]

        test_result = LoadTest.get_last_result_for(str(result2.uuid))
        expect(str(test_result.uuid)).to_equal(str(result1.uuid))

    def test_get_last_result_for_diff_only_for_same_project(self):
        config = TestConfigurationFactory.build()
        self.load_test.results.append(TestResultFactory.build(config=config))
        self.load_test.results.append(TestResultFactory.build())
        self.load_test.save()
        load_test3 = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.team.projects[1], status="Finished")
        load_test3.results.append(TestResultFactory.build(config=config))
        load_test3.save()
        load_test2 = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project, status="Finished")
        load_test2.results.append(TestResultFactory.build())
        load_test2.results.append(TestResultFactory.build(config=config))
        load_test2.save()

        result1 = self.load_test.results[0]
        result2 = load_test2.results[1]

        test_result = LoadTest.get_last_result_for(str(result2.uuid))
        expect(str(test_result.uuid)).to_equal(str(result1.uuid))

    def test_get_results_for_team_project_and_test_raise_does_not_exists_if_not_found(self):
        try:
            LoadTest.get_same_results_for_all_load_tests_from_project(self.team, "no-project", "module", "class_name", "test_name")
            assert False, "Should have raise NotFound in mongo"
        except DoesNotExist:
            assert True

    def test_get_results_for_team_project_and_test(self):
        config = TestConfigurationFactory.build()
        self.load_test.results.append(TestResultFactory.build(config=config))
        self.load_test.results.append(TestResultFactory.build())
        self.load_test.results.append(TestResultFactory.build(config=config))
        self.load_test.save()
        load_test2 = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project, status="Finished")
        load_test2.results.append(TestResultFactory.build())
        load_test2.results.append(TestResultFactory.build(config=config))
        load_test2.save()
        load_test3 = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.team.projects[1], status="Finished")
        load_test3.results.append(TestResultFactory.build(config=config))
        load_test3.results.append(TestResultFactory.build(config=config))
        load_test3.save()

        results = [str(result.uuid) for result in LoadTest.get_same_results_for_all_load_tests_from_project(self.team, self.project.name, config.module, config.class_name, config.test_name)]

        expected_results = [
            str(self.load_test.results[0].uuid),
            str(self.load_test.results[2].uuid),
            str(load_test2.results[1].uuid)
        ]

        expect(results).to_be_like(expected_results)

    def test_get_results_for_team_project_and_test_get_finished_only(self):
        config = TestConfigurationFactory.build()
        self.load_test.results.append(TestResultFactory.build(config=config))
        self.load_test.results.append(TestResultFactory.build())
        self.load_test.results.append(TestResultFactory.build(config=config))
        self.load_test.save()
        load_test2 = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project, status="Failed")
        load_test2.results.append(TestResultFactory.build())
        load_test2.results.append(TestResultFactory.build(config=config))
        load_test2.save()
        load_test3 = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project)
        load_test3.results.append(TestResultFactory.build())
        load_test3.results.append(TestResultFactory.build(config=config))
        load_test3.save()

        results = [str(result.uuid) for result in LoadTest.get_same_results_for_all_load_tests_from_project(self.team, self.project.name, config.module, config.class_name, config.test_name)]

        expected_results = [
            str(self.load_test.results[0].uuid),
            str(self.load_test.results[2].uuid),
        ]

        expect(results).to_be_like(expected_results)