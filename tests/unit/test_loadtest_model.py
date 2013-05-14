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
        self.user = UserFactory.create()
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 2)
        self.project = self.team.projects[0]
        self.test = LoadTestFactory.create(
            created_by=self.user,
            team=self.team,
            project_name=self.project.name,
            scheduled=False
        )

    def adding_to_project(self, load_tests=1, team=None, project=None):
        if not team:
            team = TeamFactory.create()

        if not project:
            TeamFactory.add_projects(team, 1)
            project = team.projects[-1]

        for i in range(load_tests):
            LoadTestFactory.create(team=team, project_name=project.name)

    def test_can_create_a_load_test(self):
        retrieveds = LoadTest.objects(id=self.test.id)
        expect(retrieveds.count()).to_equal(1)
        retrieved = retrieveds.first()
        expect(retrieved.scheduled).to_equal(False)
        expect(retrieved.created_by.email).to_equal(self.user.email)
        expect(retrieved.team.name).to_equal(self.team.name)
        expect(retrieved.project_name).to_equal(self.project.name)
        expect(retrieved.date_created).to_be_like(self.test.date_created)
        expect(retrieved.date_modified).to_be_like(self.test.date_modified)

    def test_to_dict(self):
        retrieved = LoadTest.objects(id=self.test.id).first()
        expect(retrieved.to_dict()).to_be_like(
            {
                "uuid": str(self.test.uuid),
                "createdBy": self.user.email,
                "team": self.team.name,
                "project": self.project.name,
                "scheduled": self.test.scheduled,
                "created": self.test.date_created,
                "lastModified": self.test.date_modified,
            }
        )

    def test_get_all_tests_for_a_team_and_project_ordered_by_date_created_desc(self):
        self.adding_to_project(25, self.team, self.project)
        self.adding_to_project(5, self.team, self.team.projects[1])
        loaded_tests = list(LoadTest.get_by_team_and_project(self.team, self.project.name))
        expect(loaded_tests).to_length(20)
        for load_tests in loaded_tests:
            expect(load_tests.project_name).to_equal(self.project.name)

    # def test_get_all_tests_for_a_team_ordered_by_date_created_desc(self):
    #     self.adding_to_project(7, self.team, self.project)
    #     self.adding_to_project(6, self.team, self.team.projects[1])
    #     self.adding_to_project(6)
    #     loaded_tests = list(LoadTest.get_by_team(self.team))
    #     expect(loaded_tests).to_length(10)
    #     load_tests_for_project1 = [load_test for load_test in loaded_tests if load_test.project_name == self.project.name]
    #     expect(load_tests_for_project1).to_length(5)
    #     another_project_name = self.team.projects[1].name
    #     load_tests_for_project2 = [load_test for load_test in loaded_tests if load_test.project_name == another_project_name]
    #     expect(load_tests_for_project2).to_length(5)

    # def test_get_last_tree_load_tests_for_all_projects_when_owner(self):
    #     self.add_test_to_project(5, [True, False, False, True, True], self.team, self.project)
    #     self.add_test_to_project(4, [True, True, False, False], self.team, self.team.projects[1])
    #     loaded_tests = list(LoadTest.get_all(self.user))
    #     expect(loaded_tests).to_length(6)

    # def test_get_all_scheduled_tests(self):
    #     LoadTestFactory.create(project=self.project, scheduled=True)
    #     LoadTestFactory.create(project=self.project, scheduled=False)
    #     LoadTestFactory.create(project=self.team.projects[1], scheduled=True)
    #     loaded_tests = list(LoadTest.get_scheduled())
    #     expect(loaded_tests).to_length(2)
    #
    # def test_get_all_scheduled_tests_by_projects(self):
    #     LoadTestFactory.create(project=self.project, scheduled=True)
    #     LoadTestFactory.create(project=self.project, scheduled=False)
    #     LoadTestFactory.create(project=self.team.projects[1], scheduled=True)
    #     loaded_tests = list(LoadTest.get_scheduled_by_project(self.project.name))
    #     expect(loaded_tests).to_length(1)
