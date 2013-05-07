#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com


from preggy import expect

from wight.models import User
from json import loads
from tests.unit.base import FullTestCase


class UserHandlerTest(FullTestCase):
    def setUp(self):
        super(UserHandlerTest, self).setUp()

        self.email = "user-handler-test@gmail.com"
        self.user = User.objects.filter(email=self.email).first()

        if not self.user:
            self.user = User.create(email=self.email, password="12345")

    def test_when_user_doesnt_exist(self):
        self.user = None
        response = self.fetch_with_headers("/user/info")
        expect(response.code).to_equal(401)

    def test_create_team(self):
        response = self.fetch_with_headers("/user/info")
        body = loads(response.body)
        expect(response.code).to_equal(200)
        expect(body['user']['email']).to_equal(self.email)
