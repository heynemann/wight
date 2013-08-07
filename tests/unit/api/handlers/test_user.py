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
from wight.models import User

from tests.factories import UserFactory, TeamFactory
from tests.unit.base import FullTestCase


class UserHandlerTest(FullTestCase):

    def setUp(self):
        super(UserHandlerTest, self).setUp()

        self.user = UserFactory.create(with_token=True)

    def test_when_user_doesnt_exist(self):
        self.user = None
        response = self.fetch_with_headers("/user/info/invalid@gmail.com")
        expect(response.code).to_equal(401)

    def test_get_user_info(self):
        team_owner = TeamFactory(owner=self.user)
        team_member = TeamFactory(members=[self.user])
        response = self.fetch_with_headers("/user/info/%s" % self.user.email)

        expect(response.code).to_equal(200)

        body = response.body
        if isinstance(body, six.binary_type):
            body = body.decode('utf-8')
        body = loads(body)
        expect(body['user']['email']).to_equal(self.user.email)

        owner_team = [team for team in body['user']['teams'] if team['role'] == 'owner']
        member_team = [team for team in body['user']['teams'] if team['role'] == 'member']

        expect(owner_team).to_length(1)
        expect(member_team).to_length(1)

        expect(owner_team[0]['name']).to_equal(team_owner.name)
        expect(member_team[0]['name']).to_equal(team_member.name)

    def test_change_user_password_works_with_correct_password(self):
        old_pass = "12345"
        old_salt = self.user.salt
        new_pass = "abcde"
        kwargs = {
            "old_pass": old_pass,
            "new_pass": new_pass
        }

        response = self.post("/user/change-pass/", **kwargs)
        expect(response.code).to_equal(200)
        the_user = User.objects.filter(token=self.user.token).first()

        new_hash = User.get_hash_for(the_user.salt, new_pass)
        expect(the_user.password).to_equal(new_hash)

        expect(old_salt).not_to_equal(the_user.salt)
        expect(old_pass).not_to_equal(the_user.password)

    def test_change_user_password_fails_with_wrong_password(self):
        old_pass = "67890"
        old_pass_hash = self.user.password
        old_salt = self.user.salt
        new_pass = "abcde"
        kwargs = {
            "old_pass": old_pass,
            "new_pass": new_pass
        }

        response = self.post("/user/change-pass/", **kwargs)
        expect(response.code).to_equal(403)
        the_user = User.objects.filter(token=self.user.token).first()
        pass_hash = User.get_hash_for(the_user.salt, new_pass)

        expect(str(the_user.salt)).to_equal(str(old_salt))
        expect(the_user.password).to_equal(old_pass_hash)
