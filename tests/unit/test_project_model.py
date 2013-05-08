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

from wight.models import Team
from tests.unit.base import ModelTestCase
from tests.factories import TeamFactory, UserFactory


class TestProjectModel(ModelTestCase):
    def test_can_create_project(self):
        team = TeamFactory.create()
        team.add_project(name="test-can-create-project", created_by=team.owner)

        retrieved = Team.objects.filter(name=team.name).first()
        expect(retrieved).not_to_be_null()
        expect(retrieved.projects).to_length(1)
        expect(retrieved.projects[0].name).to_equal(team.projects[0].name)

    def test_can_create_project_being_a_member(self):
        team = TeamFactory.create()
        TeamFactory.add_members(team, 2)
        team.add_project(name="test-can-create-project-being-a-member", created_by=team.members[0])

        retrieved = Team.objects.filter(name=team.name).first()
        expect(retrieved).not_to_be_null()
        expect(retrieved.projects).to_length(1)
        expect(retrieved.projects[0].name).to_equal(team.projects[0].name)

    def test_created_by_invalid_user(self):
        user = UserFactory.create()
        team = TeamFactory.create()
        try:
            team.add_project(name="test-can-create-project", created_by=user)
        except ValidationError:
            exc = sys.exc_info()[1]
            expect(str(exc)).to_include("Only the owner or members of team %s can create projects for it." % team.name)
            return

        assert False, "Should not have gotten this far"

    def test_create_project_with_same_name_in_same_team(self):
        team = TeamFactory.create()

        try:
            team.add_project(name="test-can-create-project", created_by=team.owner)
            team.add_project(name="test-can-create-project", created_by=team.owner)
        except ValueError:
            exc = sys.exc_info()[1]
            expect(exc).to_have_an_error_message_of("Can't have the same project twice in the projects collection.")
            return

        assert False, "Should not have gotten this far"

    def test_create_project_with_same_name_in_different_teams(self):
        team = TeamFactory.create()
        team2 = TeamFactory.create()

        team.add_project(name="test-can-create-project", created_by=team.owner)
        team2.add_project(name="test-can-create-project", created_by=team2.owner)

        retrieved = Team.objects.filter(name=team.name).first()
        expect(retrieved).not_to_be_null()
        expect(retrieved.projects).to_length(1)
        expect(retrieved.projects[0].name).to_equal(team.projects[0].name)

        retrieved = Team.objects.filter(name=team2.name).first()
        expect(retrieved).not_to_be_null()
        expect(retrieved.projects).to_length(1)
        expect(retrieved.projects[0].name).to_equal(team2.projects[0].name)
