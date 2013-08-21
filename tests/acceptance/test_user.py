#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys

from six import StringIO
from preggy import expect
import pexpect
from colorama import Style, Fore

from tests.acceptance.base import AcceptanceTest, ROOT_PATH
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
          +--------+--------+
          | team   | role   |
          +--------+--------+
          | %s     | owner  |
          | %s     | member |
          +--------+--------+
        """ % (self.user.email, t1.name, t2.name))

    def test_change_user_password(self):
        new_pass = "abcdef"
        child = pexpect.spawn("%s %s change-password --no-color" % (sys.executable, ROOT_PATH))
        result = StringIO()
        child.logfile = result
        child.expect("Please enter your current password:")
        child.sendline(self.password)
        child.expect("Please enter your new password:")
        child.sendline(new_pass)
        child.expect("Please enter your new password again:")
        child.sendline(new_pass)
        child.expect(pexpect.EOF)
        result = result.getvalue()
        expect(result.replace("\r", "")).to_be_like("""
            Please enter your current password: %s
            Please enter your new password: %s
            Please enter your new password again: %s
            Password changed successfully.
        """ % (self.password, new_pass, new_pass))
