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

    def handle_stdin(self, line, stdin):
        import ipdb;ipdb.set_trace()

    def test_can_register_user(self):
        self.execute("target-set", "http://localhost:2368")
        result = self.execute("login", email="acc1@gmail.com", password="password", stdin=self.handle_stdin)
        expect(result).to_equal('gahhh')

        u = User.objects.filter(email="acc1@gmail.com").first()
        expect(u).not_to_be_null()
        expect(u.token).not_to_be_null()
