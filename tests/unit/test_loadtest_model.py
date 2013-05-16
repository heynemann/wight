#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys

from preggy import expect

from wight.models import LoadTest
from tests.unit.base import ModelTestCase
from tests.factories import TeamFactory, UserFactory, LoadTestFactory


class TestCreatingLoadTestModel(ModelTestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 2)
        self.project = self.team.projects[0]

    def test_can_create_a_load_test_if_team_owner(self):
        test = LoadTestFactory.create(
            created_by=self.user,
            team=self.team,
            project_name=self.project.name,
            scheduled=False
        )
        retrieveds = LoadTest.objects(id=test.id)
        expect(retrieveds.count()).to_equal(1)
        retrieved = retrieveds.first()
        expect(retrieved.scheduled).to_equal(False)
        expect(retrieved.created_by.email).to_equal(self.user.email)
        expect(retrieved.team.name).to_equal(self.team.name)
        expect(retrieved.project_name).to_equal(self.project.name)
        expect(retrieved.date_created).to_be_like(test.date_created)
        expect(retrieved.date_modified).to_be_like(test.date_modified)

    def test_can_create_a_load_test_if_team_member(self):
        TeamFactory.add_members(self.team, 1)
        user = self.team.members[0]
        test = LoadTestFactory.create(
            created_by=user,
            team=self.team,
            project_name=self.project.name,
            scheduled=False
        )
        retrieveds = LoadTest.objects(id=test.id)
        expect(retrieveds.count()).to_equal(1)
        retrieved = retrieveds.first()
        expect(retrieved.scheduled).to_equal(False)
        expect(retrieved.created_by.email).to_equal(user.email)
        expect(retrieved.team.name).to_equal(self.team.name)
        expect(retrieved.project_name).to_equal(self.project.name)
        expect(retrieved.date_created).to_be_like(test.date_created)
        expect(retrieved.date_modified).to_be_like(test.date_modified)

    def test_cant_create_a_load_test_if_not_team_owner_or_team_member(self):
        try:
            LoadTestFactory.create(
                created_by=UserFactory.create(),
                team=self.team,
                project_name=self.project.name,
                scheduled=False
            )
        except ValueError:
            exc = sys.exc_info()[1]
            expect(str(exc)).to_include("Only the owner or members of team %s can create tests for it." % self.team.name)
            return

        assert False, "Should not have gotten this far"

    def test_to_dict(self):
        test = LoadTestFactory.create(
            created_by=self.user,
            team=self.team,
            project_name=self.project.name,
            scheduled=False,
            base_url="http://some-server.com/some-url"
        )
        retrieved = LoadTest.objects(id=test.id).first()
        expect(retrieved.to_dict()).to_be_like(
            {
                "baseUrl": "http://some-server.com/some-url",
                "uuid": str(test.uuid),
                "createdBy": self.user.email,
                "team": self.team.name,
                "project": self.project.name,
                "scheduled": test.scheduled,
                "created": test.date_created,
                "lastModified": test.date_modified,
            }
        )

    def test_get_last_20_tests_for_a_team_and_project_ordered_by_date_created_desc(self):
        LoadTestFactory.adding_to_project(25, user=self.user, team=self.team, project=self.project)
        LoadTestFactory.adding_to_project(5, user=self.user, team=self.team, project=self.team.projects[1])
        loaded_tests = list(LoadTest.get_by_team_and_project_name(self.team, self.project.name))
        expect(loaded_tests).to_length(20)
        for load_tests in loaded_tests:
            expect(load_tests.project_name).to_equal(self.project.name)

    def test_get_last_5_tests_for_a_team_ordered_by_date_created_desc(self):
        LoadTestFactory.adding_to_project(7, user=self.user, team=self.team, project=self.project)
        LoadTestFactory.adding_to_project(6, user=self.user, team=self.team, project=self.team.projects[1])
        LoadTestFactory.adding_to_project(6, user=self.user)
        loaded_tests = list(LoadTest.get_by_team(self.team))
        expect(loaded_tests).to_length(10)
        load_tests_for_project1 = [load_test for load_test in loaded_tests if load_test.project_name == self.project.name]
        expect(load_tests_for_project1).to_length(5)
        another_project_name = self.team.projects[1].name
        load_tests_for_project2 = [load_test for load_test in loaded_tests if load_test.project_name == another_project_name]
        expect(load_tests_for_project2).to_length(5)

    def test_get_last_3_load_tests_for_all_projects_when_owner(self):
        LoadTestFactory.adding_to_project(4, user=self.user, team=self.team, project=self.project)
        LoadTestFactory.adding_to_project(4, user=self.user, team=self.team, project=self.team.projects[1])
        team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(team, 1)
        LoadTestFactory.adding_to_project(4, user=self.user, team=team, project=team.projects[0])
        LoadTestFactory.adding_to_project(4, user=UserFactory.create())
        loaded_tests = list(LoadTest.get_by_user(self.user))
        expect(loaded_tests).to_length(9)

    def test_get_last_3_load_tests_for_all_projects_when_member(self):
        TeamFactory.add_members(self.team, 1)
        user = self.team.members[0]
        LoadTestFactory.adding_to_project(4, user=self.user, team=self.team, project=self.project)
        LoadTestFactory.adding_to_project(4, user=self.user, team=self.team, project=self.team.projects[1])
        team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(team, 1)
        LoadTestFactory.adding_to_project(4, user=self.user, team=team, project=team.projects[0])
        loaded_tests = list(LoadTest.get_by_user(user))
        expect(loaded_tests).to_length(6)
