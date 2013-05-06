#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import hmac
import hashlib

from preggy import expect
import six

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

    #def test_cant_create_user_with_same_email_twice(self):
        #User.create(email="repeated@gmail.com", password="12345")
        #user = User.create(email="repeated@gmail.com", password="12345")
        #expect(user).to_be_null()

    #def test_authenticating_with_wrong_pass_returns_none(self):
        #user = User(email="user2@gmail.com", password="12345")
        #user.save()

        #exists, user = User.authenticate(email="user3@gmail.com", password="12345")
        #expect(exists).to_be_false()
        #expect(user).to_be_null()
        #exists, user = User.authenticate(email="user2@gmail.com", password="54312")
        #expect(exists).to_be_true()
        #expect(user).to_be_null()

    #def test_authenticating(self):
        #user = User(email="user4@gmail.com", password="12345")
        #user.save()

        #exists, auth_user = User.authenticate(email="user4@gmail.com", password="12345")
        #expect(exists).to_be_true()
        #expect(auth_user).not_to_be_null()

        #expect(auth_user.token).not_to_be_null()
        #expect(auth_user.token_expiration).not_to_be_null()

    #def test_authenticate_using_invalid_token(self):
        #auth_user = User.authenticate_with_token(token="12312412414124")
        #expect(auth_user).to_be_null()

    #def test_authenticate_using_expired_token(self):
        #user = User(email="user6@gmail.com", password="12345")
        #user.save()

        #exists, auth_user = User.authenticate(email="user6@gmail.com", password="12345", expiration=0)
        #expect(auth_user).not_to_be_null()

        #auth_user = User.authenticate_with_token(token=auth_user.token)
        #expect(auth_user).to_be_null()

    #def test_authenticate_using_token(self):
        #user = User(email="user5@gmail.com", password="12345")
        #user.save()

        #exists, auth_user = User.authenticate(email="user5@gmail.com", password="12345")
        #expect(auth_user).not_to_be_null()

        #auth_user = User.authenticate_with_token(token=auth_user.token)
        #expect(auth_user).not_to_be_null()
