#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import User, Team
from tests.base import ModelTestCase


class TestTeamModel(ModelTestCase):
    def test_can_create_empty_team(self):
        u1 = User.create(email="team-user0@gmail.com", password="12345")
        expect(u1).not_to_be_null()
        team = Team.create(name="test-team", owner=u1)

        retrieved = Team.objects(id=team.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().name).to_equal("test-team")

        expect(retrieved.first().owner.id).to_equal(u1.id)

    def test_can_create_team_with_members(self):
        u1 = User.create(email="team-user1@gmail.com", password="12345")
        u2 = User.create(email="team-user2@gmail.com", password="12345")
        expect(u1).not_to_be_null()
        expect(u2).not_to_be_null()
        team = Team.create(name="test-team-2", owner=u1, members=[u2])

        retrieved = Team.objects(id=team.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().name).to_equal("test-team-2")
        expect(retrieved.first().members).to_length(1)
        expect(retrieved.first().members[0].email).to_equal(u2.email)

    def test_cant_create_team_with_same_name(self):
        u1 = User.create(email="team-user8@gmail.com", password="12345")
        expect(u1).not_to_be_null()
        Team.create(name="test-team-3", owner=u1)
        team = Team.create(name="test-team-3", owner=u1)
        expect(team).to_be_null()

    def test_to_dict(self):
        u1 = User.create(email="team-user3@gmail.com", password="12345")
        u2 = User.create(email="team-user4@gmail.com", password="12345")
        u3 = User.create(email="team-user5@gmail.com", password="12345")
        expect(u1).not_to_be_null()
        expect(u2).not_to_be_null()
        expect(u3).not_to_be_null()

        team = Team.create(name="test-team-to-dict-4", owner=u1, members=[u2, u3])

        expect(team.to_dict()).to_be_like({
            "name": "test-team-to-dict-4",
            "owner": "team-user3@gmail.com",
            "members": [
                "team-user4@gmail.com",
                "team-user5@gmail.com"
            ]
        })

    def test_cant_have_null_owner(self):
        pass

    def test_cant_have_same_member_twice(self):
        pass

    def test_cant_have_owner_in_members(self):
        pass
