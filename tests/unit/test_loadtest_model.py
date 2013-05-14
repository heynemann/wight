#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys

from preggy import expect
from mongoengine.base.document import ValidationError

from wight.models import Team, LoadTest
from tests.unit.base import ModelTestCase
from tests.factories import TeamFactory, UserFactory, LoadTestFactory


class TestCreatingLoadTestModel(ModelTestCase):
    def setUp(self):
        self.team = TeamFactory.create()
        TeamFactory.add_projects(self.team, 2)
        self.project = self.team.projects[0]
        self.test = LoadTestFactory.create(project=self.project, scheduled=False)

    def test_can_create_a_test(self):
        retrieved = LoadTest.objects(id=self.test.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().scheduled).to_equal(False)
        expect(retrieved.first().project.name).to_equal(self.project.name)

    def test_to_dict(self):
        retrieved = LoadTest.objects(id=self.test.id).first()
        expect(retrieved.to_dict()).to_be_like(
            {
                "team": self.team.name,
                "project": self.project.name,
                "scheduled": self.test.scheduled
            }
        )

    def test_get_projects_load_tests(self):
        LoadTestFactory.create(project=self.project, scheduled=True)
        LoadTestFactory.create(project=self.project, scheduled=True)
        LoadTestFactory.create(project=self.team.projects[1], scheduled=True)
        loaded_tests = list(LoadTest.get_by_project(self.project.name))
        expect(loaded_tests).to_length(3)

    def test_get_all_scheduled_tests(self):
        LoadTestFactory.create(project=self.project, scheduled=True)
        LoadTestFactory.create(project=self.project, scheduled=False)
        LoadTestFactory.create(project=self.team.projects[1], scheduled=True)
        loaded_tests = list(LoadTest.get_scheduled())
        expect(loaded_tests).to_length(2)

    def test_get_all_scheduled_tests_by_projects(self):
        LoadTestFactory.create(project=self.project, scheduled=True)
        LoadTestFactory.create(project=self.project, scheduled=False)
        LoadTestFactory.create(project=self.team.projects[1], scheduled=True)
        loaded_tests = list(LoadTest.get_scheduled_by_project(self.project.name))
        expect(loaded_tests).to_length(1)
