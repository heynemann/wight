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


class TestCreateProject(AcceptanceTest):

    def test_can_create_project(self):
        team = TeamFactory.create(owner=self.user)
        project_name = "test-create-project"
        repo = "repo"

        result = self.execute("project-create", team=team.name, project_name=project_name, repo=repo)
        expect(result).to_be_like(
            "Created '%s' project in '%s' team at '%s'." % (project_name, team.name, self.target)
        )

        team = Team.objects.filter(name=team.name).first()
        expect(team).not_to_be_null()

        expect(team.projects).to_length(1)
        expect(team.projects[0].name).to_equal(project_name)
        expect(team.projects[0].repository).to_equal(repo)


class TestUpdateProject(AcceptanceTest):
    def setUp(self):
        super(TestUpdateProject, self).setUp()
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 1)
        self.project = self.team.projects[0]

    def test_can_update_project(self):
        result = self.execute(
            "project-update",
            team=self.team.name,
            project=self.project.name,
            project_name="new-project-name",
            repo="new-repo"
        )
        expect(result).to_be_like(
            "Updated '%s' project in '%s' team at '%s'." % ("new-project-name", self.team.name, self.target)
        )
        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects[0].name).to_equal("new-project-name")
        expect(team.projects[0].repository).to_equal("new-repo")

    def test_can_update_project_with_name_only(self):
        result = self.execute(
            "project-update",
            team=self.team.name,
            project=self.project.name,
            project_name="new-project-name"
        )
        expect(result).to_be_like(
            "Updated '%s' project in '%s' team at '%s'." % ("new-project-name", self.team.name, self.target)
        )
        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects[0].name).to_equal("new-project-name")
        expect(team.projects[0].repository).to_equal(self.project.repository)

    def test_can_update_project_with_repository_only(self):
        result = self.execute(
            "project-update",
            team=self.team.name,
            project=self.project.name,
            repo="new-repo"
        )
        expect(result).to_be_like(
            "Updated '%s' project in '%s' team at '%s'." % (self.project.name, self.team.name, self.target)
        )
        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects[0].name).to_equal(self.project.name)
        expect(team.projects[0].repository).to_equal("new-repo")


class TestDeleteProject(AcceptanceTest):
    def setUp(self):
        super(TestDeleteProject, self).setUp()
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 1)
        self.project = self.team.projects[0]

    def test_can_delete_project(self):
        result = self.execute(
            "project-delete",
            team=self.team.name,
            project=self.project.name,
            stdin=['y']
        )
        expect(result).to_be_like(
            """
            This operation will delete the project '%s' and all its tests.
            Are you sure you want to delete project '%s'? [y/n]
            Deleted '%s' project and tests for team '%s' in '%s' target.
            """ % (self.project.name, self.project.name, self.project.name, self.team.name, self.target)
        )
        team = Team.objects.filter(name=self.team.name).first()
        expect(team.projects).to_length(0)
