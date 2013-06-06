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
        TeamFactory.add_projects(self.team, 1)
        self.project = self.team.projects[0]
        self.load_test = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project)

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
        load_test2 = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project)
        load_test2.results.append(TestResultFactory.build())
        load_test2.results.append(TestResultFactory.build(config=config))
        load_test2.save()

        result1 = self.load_test.results[0]
        result2 = load_test2.results[1]

        test_result = LoadTest.get_last_result_for(str(result2.uuid))
        expect(str(test_result.uuid)).to_equal(str(result1.uuid))
