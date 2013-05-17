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
                "created": test.date_created.isoformat()[:19],
                "lastModified": test.date_modified.isoformat()[:19],
            }
        )

    def test_get_last_20_tests_for_a_team_and_project_ordered_by_date_created_desc(self):
        LoadTestFactory.add_to_project(25, user=self.user, team=self.team, project=self.project)
        LoadTestFactory.add_to_project(5, user=self.user, team=self.team, project=self.team.projects[1])
        loaded_tests = list(LoadTest.get_by_team_and_project_name(self.team, self.project.name))
        expect(loaded_tests).to_length(20)
        for load_tests in loaded_tests:
            expect(load_tests.project_name).to_equal(self.project.name)

    def test_get_last_5_tests_for_a_team_ordered_by_date_created_desc(self):
        LoadTestFactory.add_to_project(7, user=self.user, team=self.team, project=self.project)
        LoadTestFactory.add_to_project(6, user=self.user, team=self.team, project=self.team.projects[1])
        LoadTestFactory.add_to_project(6, user=self.user)
        loaded_tests = list(LoadTest.get_by_team(self.team))
        expect(loaded_tests).to_length(10)
        load_tests_for_project1 = [load_test for load_test in loaded_tests if load_test.project_name == self.project.name]
        expect(load_tests_for_project1).to_length(5)
        another_project_name = self.team.projects[1].name
        load_tests_for_project2 = [load_test for load_test in loaded_tests if load_test.project_name == another_project_name]
        expect(load_tests_for_project2).to_length(5)

    def test_get_last_3_load_tests_for_all_projects_when_owner(self):
        LoadTestFactory.add_to_project(4, user=self.user, team=self.team, project=self.project)
        LoadTestFactory.add_to_project(4, user=self.user, team=self.team, project=self.team.projects[1])
        team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(team, 1)
        LoadTestFactory.add_to_project(4, user=self.user, team=team, project=team.projects[0])
        LoadTestFactory.add_to_project(4, user=UserFactory.create())
        loaded_tests = list(LoadTest.get_by_user(self.user))
        expect(loaded_tests).to_length(9)

    def test_get_last_3_load_tests_for_all_projects_when_member(self):
        TeamFactory.add_members(self.team, 1)
        user = self.team.members[0]
        LoadTestFactory.add_to_project(4, user=self.user, team=self.team, project=self.project)
        LoadTestFactory.add_to_project(4, user=self.user, team=self.team, project=self.team.projects[1])
        team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(team, 1)
        LoadTestFactory.add_to_project(4, user=self.user, team=team, project=team.projects[0])
        loaded_tests = list(LoadTest.get_by_user(user))
        expect(loaded_tests).to_length(6)


class TestLoadFromFunkloadResult(ModelTestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 2)
        self.project = self.team.projects[0]

    def test_can_parse_configuration_from_funkload_result(self):
        test = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project)

        config = {
            u'class': u'HealthCheckTest',
            u'class_description': u'Testando se o healthcheck aguenta carga.',
            u'class_title': u'HealthCheck Tests',
            u'configuration_file': u'/private/var/folders/th/z6vmj34j1gngpvwl5fg5t9440000gp/T/tmprkUn7b/HealthCheckTest.conf',
            u'cycle_time': u'1.0',
            u'cycles': u'[10, 20]',
            u'description': u'Testando se o healthcheck aguenta carga.',
            u'duration': u'5',
            u'id': u'test_healthcheck',
            u'log_xml': u'/private/var/folders/th/z6vmj34j1gngpvwl5fg5t9440000gp/T/tmprkUn7b/funkload.xml',
            u'method': u'test_healthcheck',
            u'module': u'test_healthcheck',
            u'node': u'HeynemannMBP',
            u'python_version': u'2.7.3',
            u'server_url': u'http://localhost:2368',
            u'sleep_time': u'0.01',
            u'sleep_time_max': u'0.5',
            u'sleep_time_min': u'0.0',
            u'startup_delay': u'0.01',
            'time': u'2013-05-17T17:39:01.511075',
            'version': u'1.16.1'
        }
        cycles = {}

        test.add_result(config, cycles)

        loaded_test = LoadTest.objects(uuid=test.uuid).first()

        expect(loaded_test).not_to_be_null()

        expect(loaded_test.config).not_to_be_null()
        cfg = loaded_test.config

        expect(cfg.title).to_equal(config['class_title'])
        expect(cfg.description).to_equal(config['class_description'])

        expect(cfg.module).to_equal(config['module'])
        expect(cfg.class_name).to_equal(config['class'])
        expect(cfg.test_name).to_equal(config['method'])

        expect(cfg.target_server).to_equal(config['server_url'])
        expect(cfg.cycles).to_equal(config['cycles'])
        expect(cfg.cycle_duration).to_equal(int(config['duration']))

        expect(cfg.sleep_time).to_equal(float(config['sleep_time']))
        expect(cfg.sleep_time_min).to_equal(float(config['sleep_time_min']))
        expect(cfg.sleep_time_max).to_equal(float(config['sleep_time_max']))

        expect(cfg.startup_delay).to_equal(float(config['startup_delay']))

        expect(cfg.test_date.isoformat()[:20]).to_equal(config['time'][:20])
        expect(cfg.funkload_version).to_equal(config['version'])
