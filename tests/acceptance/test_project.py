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
from tests.factories import TeamFactory


class TestProject(AcceptanceTest):

    def test_can_create_project(self):
        team = TeamFactory.create(owner=self.user)
        project_name = "test-create-project"
        repo = "repo"

        result = self.execute("create-project", team=team.name, project_name=project_name, repo=repo)
        expect(result).to_equal("Created '%s' project in '%s' team at '%s'." % (project_name, team.name, self.target))

        team = Team.objects.filter(name=team.name).first()
        expect(team).not_to_be_null()

        expect(team.projects).to_length(1)
        expect(team.projects[0].name).to_equal(project_name)
        expect(team.projects[0].repository).to_equal(repo)

    #def test_can_show_team(self):
        #team = TeamFactory.create(owner=self.user)

        #result = self.execute("team-show", team.name)
        #expect(result).to_be_like("""
        #%s
        #%s

        #Team members:
        #+--------------------------------+-------+
        #| user                           |  role |
        #+--------------------------------+-------+
        #| %s                             | owner |
        #+--------------------------------+-------+
        #""" % (team.name, "=" * len(team.name), self.username))

    #def test_can_update_team(self):
        #team = TeamFactory.create(owner=self.user)

        #result = self.execute("team-update", team.name, "new-team-name")
        #expect(result).to_equal("Updated '%s' team to 'new-team-name' in '%s' target." % (team.name, self.target))

        #team = Team.objects.filter(name="new-team-name").first()
        #expect(team).not_to_be_null()

    #def test_can_add_user(self):
        #team = TeamFactory.create(owner=self.user)
        #user = UserFactory.create()

        #result = self.execute("team-adduser", team.name, user.email)
        #expect(result).to_equal("User '%s' added to Team '%s'." % (user.email, team.name))

        #team = Team.objects.filter(name=team.name).first()
        #expect(team.members).to_include(user)

    #def test_can_delete_team(self):
        #team = TeamFactory.create(owner=self.user)

        #result = self.execute("team-delete", team.name, stdin=[team.name])
        #expect(result).to_be_like(
            #"""
                #This operation will delete all projects and all tests of team '%s'.
                #You have to retype the team name to confirm deletion.

                #Team name:  Deleted '%s' team, all its projects and tests in '%s' target.
            #""" % (team.name, team.name, self.target))

        #team = Team.objects.filter(name=team.name).first()
        #expect(team).to_be_null()
