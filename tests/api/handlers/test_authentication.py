#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import User
from tests.base import ApiTestCase


class UserAuthenticationTest(ApiTestCase):
    def get_app(self):
        return self.make_app()

    def test_authenticate_with_valid_user(self):
        user = User(email="test_auth1@gmail.com", password="12345")
        user.save()

        response = self.fetch('/auth/user/?username=test_auth1@gmail.com&password=12345')
        expect(response.code).to_equal(200)

        user = User.objects.filter(email="test_auth1@gmail.com")
        expect(response.body).to_be_like(user.first().token)
