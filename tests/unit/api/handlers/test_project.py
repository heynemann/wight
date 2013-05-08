#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import Team
from tests.unit.base import FullTestCase
from tests.factories import TeamFactory, UserFactory


class TeamProjectTest(FullTestCase):
    def setUp(self):
        super(TeamProjectTest, self).setUp()

        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_members(self.team, 2)

    def test_create_project_being_owner(self):
        project_name = "project_test_being_owner"
        response = self.post("/teams/%s/projects/" % self.team.name, name=project_name, repository="test")
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        team = Team.objects.filter(name=self.team.name).first()
        expect(team).not_to_be_null()
        expect(team.projects).to_length(1)
        expect(team.projects[0].name).to_equal(project_name)
        expect(team.projects[0].repository).to_equal("test")

    def test_create_project_being_team_member(self):
        self.user = self.team.members[0]
        self.user.validate_token()
        self.user.save()

        project_name = "project_test_being_member"
        response = self.post("/teams/%s/projects/" % self.team.name, name=project_name, repository="test2")
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        team = Team.objects.filter(name=self.team.name).first()
        expect(team).not_to_be_null()
        expect(team.projects).to_length(1)
        expect(team.projects[0].name).to_equal(project_name)
        expect(team.projects[0].repository).to_equal("test2")

    def test_cant_create_project_without_being_auth(self):
        self.user = None
        response = self.post("/teams/%s/projects/" % self.team.name, name="new-name", repository="test")
        expect(response.code).to_equal(401)

    def test_cant_create_project_without_name(self):
        response = self.post("/teams/%s/projects/" % self.team.name, name="", repository="repo")
        expect(response.code).to_equal(400)

        response = self.post("/teams/%s/projects/" % self.team.name, repository="repo")
        expect(response.code).to_equal(400)

    def test_cant_create_project_without_repo(self):
        response = self.post("/teams/%s/projects/" % self.team.name, name="without-repo", repository="")
        expect(response.code).to_equal(400)

        response = self.post("/teams/%s/projects/" % self.team.name, name="without-repo")
        expect(response.code).to_equal(400)

    def test_cant_create_project_for_invalid_team(self):
        response = self.post("/teams/invalid-team/projects/", name="valid-name", repository="repo")
        expect(response.code).to_equal(404)

    def test_cant_create_project_without_being_in_the_team(self):
        self.user = UserFactory.create(with_token=True)

        project_name = "project_test"
        response = self.post("/teams/%s/projects/" % self.team.name, name=project_name, repository="repo")
        expect(response.code).to_equal(403)
