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

from tests.factories import UserFactory
from tests.unit.base import FullTestCase


class UserHandlerTest(FullTestCase):
    def setUp(self):
        super(UserHandlerTest, self).setUp()

        self.user = UserFactory.create()

    def test_when_user_doesnt_exist(self):
        self.user = None
        response = self.fetch_with_headers("/user/info")
        expect(response.code).to_equal(401)

    def test_create_team(self):
        response = self.fetch_with_headers("/user/info")
        body = response.body
        if isinstance(body, six.binary_type):
            body = body.decode('utf-8')
        body = loads(body)
        expect(response.code).to_equal(200)
        expect(body['user']['email']).to_equal(self.email)
