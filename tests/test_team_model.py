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
        team = Team.create(name="test-team")

        retrieved = Team.objects(id=team.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().name).to_equal("test-team")

    def test_can_create_team_with_members(self):
        u1 = User.create(email="team-user1@gmail.com", password="12345")
        u2 = User.create(email="team-user2@gmail.com", password="12345")
        team = Team.create(name="test-team-2", members=[u1, u2])

        retrieved = Team.objects(id=team.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().name).to_equal("test-team-2")
        expect(retrieved.first().members).to_length(2)
        expect(retrieved.first().members[0].email).to_equal(u1.email)
        expect(retrieved.first().members[1].email).to_equal(u2.email)

    def test_cant_create_team_with_same_name(self):
        Team.create(name="test-team-3")
        team = Team.create(name="test-team-3")
        expect(team).to_be_null()

    def test_to_dict(self):
        u1 = User.create(email="team-user3@gmail.com", password="12345")
        u2 = User.create(email="team-user4@gmail.com", password="12345")
        team = Team.create(name="test-team-to-dict-4", members=[u1, u2])

        expect(team.to_dict()).to_be_like({
            "name": "test-team-to-dict-4",
            "members": [
                "team-user3@gmail.com",
                "team-user4@gmail.com"
            ]
        })
