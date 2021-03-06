#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import Team
from tests.acceptance.base import AcceptanceTest
from tests.factories import TeamFactory, UserFactory


class TestTeam(AcceptanceTest):

    def test_can_create_team(self):
        team_name = "test-create-team"

        result = self.execute("team-create", team_name)
        expect(result).to_be_like("Created 'test-create-team' team in '%s' target." % self.target)

        team = Team.objects.filter(name=team_name).first()
        expect(team).not_to_be_null()

    def test_can_show_team(self):
        team = TeamFactory.create(owner=self.user)

        result = self.execute("team-show", team.name)
        expect(result).to_be_like("""
        %s
        %s

        +--------------------------------+-------+
        | user                           |  role |
        +--------------------------------+-------+
        | %s                             | owner |
        +--------------------------------+-------+
        This team has no projects. To create a project use 'wight project-create'.
        """ % (team.name, "-" * len(team.name), self.username))

    def test_can_update_team(self):
        team = TeamFactory.create(owner=self.user)

        result = self.execute("team-update", team.name, "new-team-name")
        expect(result).to_be_like("Updated '%s' team to 'new-team-name' in '%s' target." % (team.name, self.target))

        team = Team.objects.filter(name="new-team-name").first()
        expect(team).not_to_be_null()

    def test_can_add_user(self):
        team = TeamFactory.create(owner=self.user)
        user = UserFactory.create()

        result = self.execute("team-adduser", team.name, user.email)
        expect(result).to_be_like("User '%s' added to Team '%s'." % (user.email, team.name))

        team = Team.objects.filter(name=team.name).first()
        expect(team.members).to_include(user)

    def test_can_remove_user(self):
        user = UserFactory.create()
        team = TeamFactory.create(owner=self.user, members=[user])

        result = self.execute("team-removeuser", team.name, user.email)
        expect(result).to_be_like("User '%s' removed from Team '%s'." % (user.email, team.name))

        team = Team.objects.filter(name=team.name).first()
        expect(team.members).not_to_include(user)

    def test_can_delete_team(self):
        team = TeamFactory.create(owner=self.user)

        result = self.execute("team-delete", team.name, stdin=[team.name])
        expect(result).to_be_like(
            """
                This operation will delete all projects and all tests of team '%s'.
                You have to retype the team name to confirm deletion.

                Team name:  Deleted '%s' team, all its projects and tests in '%s' target.
            """ % (team.name, team.name, self.target))

        team = Team.objects.filter(name=team.name).first()
        expect(team).to_be_null()
