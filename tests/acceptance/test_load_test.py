#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from tests.acceptance.base import AcceptanceTest
from tests.factories import TeamFactory, LoadTestFactory, UserFactory
from wight.models import LoadTest


class TestLoadTest(AcceptanceTest):

    def test_list_gets_403_if_not_team_member(self):
        team = TeamFactory.create(owner=UserFactory.create())
        TeamFactory.add_projects(team, 1)
        project = team.projects[0]
        LoadTestFactory.add_to_project(25, user=self.user, team=team, project=project)
        result = self.execute("list", team=team.name)
        expect(result).to_be_like("Your are not the owner or team member for the team '%s' and cannot list its tests in target '%s'." % (team.name, self.target))

    def test_list_load_tests_by_team_and_project(self):
        team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(team, 1)
        project = team.projects[0]
        LoadTestFactory.add_to_project(25, user=self.user, team=team, project=project)

        load_tests = LoadTest.get_sliced_by_team_and_project_name(team, project.name, 20)
        uuids = ["| %s | Scheduled | wight show %s |" % (load.uuid, load.uuid) for load in load_tests]

        result = self.execute("list", team=team.name, project=project.name)
        expect(result).to_be_like("""
            Team: %s ---- Project: %s
            +--------------------------------------+-----------+-------------------------------------------------+
            | uuid                                 |   status  |                                                 |
            +--------------------------------------+-----------+-------------------------------------------------+
            %s
            +--------------------------------------+-----------+-------------------------------------------------+
        """ % (team.name, project.name, "".join(uuids))
        )

    def test_list_load_tests_by_team_only(self):
        team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(team, 2)
        project1 = team.projects[0]
        project2 = team.projects[1]
        LoadTestFactory.add_to_project(7, user=self.user, team=team, project=project1)
        LoadTestFactory.add_to_project(7, user=self.user, team=team, project=project2)

        load_tests1 = LoadTest.get_sliced_by_team_and_project_name(team, project1.name, 5)
        load_tests2 = LoadTest.get_sliced_by_team_and_project_name(team, project2.name, 5)

        uuids1 = ["| %s | Scheduled | wight show %s |" % (load.uuid, load.uuid) for load in load_tests1]
        uuids2 = ["| %s | Scheduled | wight show %s |" % (load.uuid, load.uuid) for load in load_tests2]

        result = self.execute("list", team=team.name)
        expect(result).to_be_like("""
            Team: %s ---- Project: %s
            +--------------------------------------+-----------+-------------------------------------------------+
            | uuid                                 |   status  |                                                 |
            +--------------------------------------+-----------+-------------------------------------------------+
            %s
            +--------------------------------------+-----------+-------------------------------------------------+

            Team: %s ---- Project: %s
            +--------------------------------------+-----------+-------------------------------------------------+
            | uuid                                 |   status  |                                                 |
            +--------------------------------------+-----------+-------------------------------------------------+
            %s
            +--------------------------------------+-----------+-------------------------------------------------+
        """ % (team.name, project1.name, "".join(uuids1), team.name, project2.name, "".join(uuids2))
        )

    def test_list_load_tests_by_user_only(self):
        team1 = TeamFactory.create(owner=self.user)
        team2 = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(team1, 2)
        TeamFactory.add_projects(team2, 3)

        project1 = team1.projects[0]
        project2 = team1.projects[1]

        project3 = team2.projects[0]
        project4 = team2.projects[1]
        project5 = team2.projects[2]

        LoadTestFactory.add_to_project(4, user=self.user, team=team1, project=project1)
        LoadTestFactory.add_to_project(4, user=self.user, team=team1, project=project2)

        LoadTestFactory.add_to_project(4, user=self.user, team=team2, project=project3)
        LoadTestFactory.add_to_project(4, user=self.user, team=team2, project=project4)
        LoadTestFactory.add_to_project(4, user=self.user, team=team2, project=project5)

        load_tests1 = LoadTest.get_sliced_by_team_and_project_name(team1, project1.name, 3)
        load_tests2 = LoadTest.get_sliced_by_team_and_project_name(team1, project2.name, 3)

        load_tests3 = LoadTest.get_sliced_by_team_and_project_name(team2, project3.name, 3)
        load_tests4 = LoadTest.get_sliced_by_team_and_project_name(team2, project4.name, 3)
        load_tests5 = LoadTest.get_sliced_by_team_and_project_name(team2, project5.name, 3)

        uuids1 = ["| %s | Scheduled | wight show %s |" % (load.uuid, load.uuid) for load in load_tests1]
        uuids2 = ["| %s | Scheduled | wight show %s |" % (load.uuid, load.uuid) for load in load_tests2]

        uuids3 = ["| %s | Scheduled | wight show %s |" % (load.uuid, load.uuid) for load in load_tests3]
        uuids4 = ["| %s | Scheduled | wight show %s |" % (load.uuid, load.uuid) for load in load_tests4]
        uuids5 = ["| %s | Scheduled | wight show %s |" % (load.uuid, load.uuid) for load in load_tests5]

        result = self.execute("list")
        expect(result).to_be_like("""
            Team: %s ---- Project: %s
            +--------------------------------------+-----------+-------------------------------------------------+
            | uuid                                 |   status  |                                                 |
            +--------------------------------------+-----------+-------------------------------------------------+
            %s
            +--------------------------------------+-----------+-------------------------------------------------+

            Team: %s ---- Project: %s
            +--------------------------------------+-----------+-------------------------------------------------+
            | uuid                                 |   status  |                                                 |
            +--------------------------------------+-----------+-------------------------------------------------+
            %s
            +--------------------------------------+-----------+-------------------------------------------------+

            Team: %s ---- Project: %s
            +--------------------------------------+-----------+-------------------------------------------------+
            | uuid                                 |   status  |                                                 |
            +--------------------------------------+-----------+-------------------------------------------------+
            %s
            +--------------------------------------+-----------+-------------------------------------------------+

            Team: %s ---- Project: %s
            +--------------------------------------+-----------+-------------------------------------------------+
            | uuid                                 |   status  |                                                 |
            +--------------------------------------+-----------+-------------------------------------------------+
            %s
            +--------------------------------------+-----------+-------------------------------------------------+

            Team: %s ---- Project: %s
            +--------------------------------------+-----------+-------------------------------------------------+
            | uuid                                 |   status  |                                                 |
            +--------------------------------------+-----------+-------------------------------------------------+
            %s
            +--------------------------------------+-----------+-------------------------------------------------+
        """ % (
            team1.name, project1.name, "".join(uuids1),
            team1.name, project2.name, "".join(uuids2),
            team2.name, project3.name, "".join(uuids3),
            team2.name, project4.name, "".join(uuids4),
            team2.name, project5.name, "".join(uuids5)
        )
        )
