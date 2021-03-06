#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from json import loads

from preggy import expect
import six

from wight.models import Team
from tests.unit.base import FullTestCase
from tests.factories import TeamFactory, UserFactory, ProjectFactory


class ShowTeamProjectTest(FullTestCase):
    def setUp(self):
        super(ShowTeamProjectTest, self).setUp()

        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_members(self.team, 2)

    def test_cant_get_if_not_authenticated(self):
        self.user = None
        response = self.fetch_with_headers("/teams/%s/projects/%s" % (self.team.name, "whatever"))
        expect(response.code).to_equal(401)

    def test_cant_get_if_not_team_member(self):
        self.user = UserFactory(with_token=True)
        response = self.fetch_with_headers("/teams/%s/projects/%s" % (self.team.name, "whatever"))
        expect(response.code).to_equal(403)

    def test_get_project_by_team_and_name_return_200_if_no_errors(self):
        TeamFactory.add_projects(self.team, 2)
        project = self.team.projects[1]
        response = self.fetch_with_headers("/teams/%s/projects/%s" % (self.team.name, project.name))
        expect(response.code).to_equal(200)

    def test_get_project_by_team_should_be_a_json(self):
        TeamFactory.add_projects(self.team, 2)
        project = self.team.projects[1]
        response = self.fetch_with_headers("/teams/%s/projects/%s" % (self.team.name, project.name))
        expect(response.code).to_equal(200)
        obj = response.body
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')
        try:
            loads(obj)
            assert True
        except ValueError:
            raise AssertionError("Should be possible to load a json from response")

    def test_get_project_by_team_should_be_a_equal_to_project_dict(self):
        TeamFactory.add_projects(self.team, 2)
        project = self.team.projects[1]
        response = self.fetch_with_headers("/teams/%s/projects/%s" % (self.team.name, project.name))
        expect(response.code).to_equal(200)
        obj = response.body
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')
        expect(loads(obj)).to_be_like(project.to_dict())

    def test_should_return_404_if_project_not_in_team(self):
        response = self.fetch_with_headers("/teams/%s/projects/%s" % (self.team.name, "whatever"))
        expect(response.code).to_equal(404)


class CreateTeamProjectTest(FullTestCase):
    def setUp(self):
        super(CreateTeamProjectTest, self).setUp()

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

    def test_create_project_twice_in_the_same_team(self):
        project_name = "same-project-twice"
        self.team.add_project(project_name, "repo", self.team.owner)

        response = self.post("/teams/%s/projects/" % self.team.name, name=project_name, repository="repo")
        expect(response.code).to_equal(409)


class UpdateTeamProjectTest(FullTestCase):
    def setUp(self):
        super(UpdateTeamProjectTest, self).setUp()

        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 1)
        TeamFactory.add_members(self.team, 2)
        self.project = self.team.projects[0]

    def test_cant_update_project_without_being_auth(self):
        self.user = None
        response = self.put("/teams/%s/projects/%s" % (self.team.name, self.project.name), name="new-name", repository="test")
        expect(response.code).to_equal(401)

    def test_cant_update_project_without_being_in_the_team(self):
        self.user = UserFactory.create(with_token=True)
        response = self.put("/teams/%s/projects/%s" % (self.team.name, self.project.name), name="new-name", repository="repo")
        expect(response.code).to_equal(403)

    def test_update_project_being_owner(self):
        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects).to_length(1)
        project_name = "new_project_test_being_owner"
        response = self.put("/teams/%s/projects/%s" % (self.team.name, self.project.name), name=project_name, repository="test")
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")
        team = Team.objects.filter(name=self.team.name).first()
        expect(team).not_to_be_null()
        expect(team.projects).to_length(1)
        expect(team.projects[0].name).to_equal(project_name)
        expect(team.projects[0].repository).to_equal("test")

    def test_update_project_being_team_member(self):
        self.user = self.team.members[0]
        self.user.validate_token()
        self.user.save()

        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects).to_length(1)
        project_name = "new_project_test_being_owner"
        response = self.put("/teams/%s/projects/%s" % (self.team.name, self.project.name), name=project_name, repository="test")
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")
        team = Team.objects.filter(name=self.team.name).first()
        expect(team).not_to_be_null()
        expect(team.projects).to_length(1)
        expect(team.projects[0].name).to_equal(project_name)
        expect(team.projects[0].repository).to_equal("test")

    def test_can_update_project_without_name(self):
        response = self.put("/teams/%s/projects/%s" % (self.team.name, self.project.name), repository="test")
        expect(response.code).to_equal(200)
        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects[0].name).to_equal(self.project.name)
        expect(team.projects[0].repository).to_equal("test")

    def test_can_update_project_without_repo(self):
        response = self.put("/teams/%s/projects/%s" % (self.team.name, self.project.name), name="test")
        expect(response.code).to_equal(200)
        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects[0].name).to_equal("test")
        expect(team.projects[0].repository).to_equal(self.project.repository)

    def test_cant_update_project_for_invalid_team(self):
        response = self.put("/teams/invalid-team/projects/%s" % self.project.name, name="test")
        expect(response.code).to_equal(404)

    def test_cant_update_a_non_existing_project(self):
        response = self.put("/teams/%s/projects/non_ecxists_project" % self.team.name, name="test")
        expect(response.code).to_equal(404)
        expect(response.body).to_equal("Project with name 'non_ecxists_project' was not found.")


class DeleteTeamProjectTest(FullTestCase):
    def setUp(self):
        super(DeleteTeamProjectTest, self).setUp()

        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 1)
        TeamFactory.add_members(self.team, 2)
        self.project = self.team.projects[0]

    def test_cant_delete_project_without_being_auth(self):
        self.user = None
        response = self.delete("/teams/%s/projects/%s" % (self.team.name, self.project.name))
        expect(response.code).to_equal(401)

    def test_cant_delete_project_without_being_in_the_team(self):
        self.user = UserFactory.create(with_token=True)
        response = self.delete("/teams/%s/projects/%s" % (self.team.name, self.project.name))
        expect(response.code).to_equal(403)

    def test_delete_project_being_owner(self):
        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects).to_length(1)
        response = self.delete("/teams/%s/projects/%s" % (self.team.name, self.project.name))
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")
        team = Team.objects.filter(name=self.team.name).first()
        expect(team).not_to_be_null()
        expect(team.projects).to_length(0)

    def test_delete_project_being_team_member(self):
        self.user = self.team.members[0]
        self.user.validate_token()
        self.user.save()
        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects).to_length(1)
        response = self.delete("/teams/%s/projects/%s" % (self.team.name, self.project.name))
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")
        team = Team.objects.filter(name=self.team.name).first()
        expect(team).not_to_be_null()
        expect(team.projects).to_length(0)

    def test_cant_delete_project_for_invalid_team(self):
        response = self.delete("/teams/invalid-team/projects/%s" % self.project.name)
        expect(response.code).to_equal(404)
