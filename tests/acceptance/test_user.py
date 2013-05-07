#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from tests.acceptance.base import AcceptanceTest


class TestUser(AcceptanceTest):

    def test_can_get_user_email(self):
        result = self.execute("user-info")
        expect(result).to_equal("User: %s" % self.user.email)
