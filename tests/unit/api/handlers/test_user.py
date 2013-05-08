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

from tests.factories import UserFactory, TeamFactory
from tests.unit.base import FullTestCase


class UserHandlerTest(FullTestCase):
    def setUp(self):
        super(UserHandlerTest, self).setUp()

        self.user = UserFactory.create(with_token=True)

    def test_when_user_doesnt_exist(self):
        self.user = None
        response = self.fetch_with_headers("/user/info")
        expect(response.code).to_equal(401)

    def test_get_user_info(self):
        team_owner = TeamFactory(owner=self.user)
        team_member = TeamFactory(members=[self.user])
        response = self.fetch_with_headers("/user/info")

        expect(response.code).to_equal(200)

        body = response.body
        if isinstance(body, six.binary_type):
            body = body.decode('utf-8')
        body = loads(body)
        expect(body['user']['email']).to_equal(self.user.email)
        expect(body['user']['teams'][0]['name']).to_equal(team_owner.name)
        expect(body['user']['teams'][0]['role']).to_equal('owner')
        expect(body['user']['teams'][1]['name']).to_equal(team_member.name)
        expect(body['user']['teams'][1]['role']).to_equal('member')
