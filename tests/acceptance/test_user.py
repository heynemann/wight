#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from tests.acceptance.base import AcceptanceTest
from tests.factories import TeamFactory, UserFactory


class TestUser(AcceptanceTest):

    def test_can_get_user_email(self):
        result = self.execute("user-info")
        expect(result).to_be_like("""User: %s
          +------+------+
          | team | role |
          +------+------+
          +------+------+
        """ % self.user.email)

    def test_show_memberships(self):
        t1 = TeamFactory.create(owner=self.user)
        t2 = TeamFactory.create(members=[self.user])
        result = self.execute("user-info")
        expect(result).to_be_like("""User: %s
          +---------+--------+
          | team    | role   |
          +---------+--------+
          | %s      | owner  |
          | %s      | member |
          +---------+--------+
        """ % (self.user.email, t1.name, t2.name))

    # TODO: isso aqui quebra
    # def test_change_user_password(self):
    #     new_pass = "abcdef"
    #     stdin =  [self.password, new_pass, new_pass]
    #     result = self.execute("change-password", stdin=stdin)
    #     expect(result).to_equal("Password changed successfuly.")