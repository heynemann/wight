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


class TestTeamModel(ModelTestCase):
    def test_can_create_empty_team(self):
        team = TeamFactory.create()

        retrieved = Team.objects(id=team.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().name).to_equal(team.name)

        expect(retrieved.first().owner.id).to_equal(team.owner.id)

    def test_can_create_team_with_members(self):
        team = TeamFactory.create()
        TeamFactory.add_members(team, 1)

        retrieved = Team.objects(id=team.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().name).to_equal(team.name)
        expect(retrieved.first().members).to_length(1)
        expect(retrieved.first().members[0].email).to_equal(team.members[0].email)

    def test_cant_create_team_with_same_name(self):
        team = TeamFactory.create()
        team = Team.create(name=team.name, owner=team.owner)
        expect(team).to_be_null()

    def test_to_dict(self):
        team = TeamFactory.create()
        TeamFactory.add_members(team, 2)

        expect(team.to_dict()).to_be_like({
            "name": team.name,
            "owner": team.owner.email,
            "members": [
                team.members[0].email,
                team.members[1].email,
            ]
        })

    def test_cant_have_null_owner(self):
        try:
            Team.create(name="null-owner-5", owner=None)
        except ValidationError:
            return
        assert False, "Should not have gotten this far"

    def test_cant_have_same_member_twice(self):
        u1 = UserFactory.create()
        u2 = UserFactory.create()

        try:
            Team.create(name="test-team-5", owner=u1, members=[u2, u2])
        except ValueError:
            ex = sys.exc_info()[1]
            expect(ex).to_have_an_error_message_of("Can't have the same user twice in the members collection.")
            return
        assert False, "Should not have gotten this far"

    def test_cant_have_owner_in_members(self):
        u1 = UserFactory.create()

        try:
            Team.create(name="test-team-5", owner=u1, members=[u1])
        except ValueError:
            ex = sys.exc_info()[1]
            expect(ex).to_have_an_error_message_of("Can't have a team owner in the members collection.")
            return

        assert False, "Should not have gotten this far"
