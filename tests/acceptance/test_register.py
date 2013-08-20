#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import User
from tests.acceptance.base import AcceptanceTest


class TestRegisterUser(AcceptanceTest):

    def test_can_register_user(self):
        # Set target to acc target
        self.execute("target-set", "http://localhost:2368")

        # authenticates
        result = self.execute("login", "acc1@gmail.com", password="password", stdin=['y'])
        expect(result).to_be_like('User does not exist. Do you wish to register? [y/n] User registered and authenticated.')

        # user is in mongodb?
        u = User.objects.filter(email="acc1@gmail.com").first()
        expect(u).not_to_be_null()
        expect(u.token).not_to_be_null()
