#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import UserData
from tests.acceptance.base import AcceptanceTest


class TestTarget(AcceptanceTest):

    def test_can_set_target(self):
        target = "http://my-test-target:2324"

        # Set target to acc target
        result = self.execute("target-set", target)
        expected = "Wight target set to '%s'. In order to login with wight, use 'wight login'."
        expect(result).to_be_like(expected % target)

        ud = UserData.load()
        expect(ud.target).to_be_like(target)

    def test_can_get_empty_target(self):
        self.clear_user_data()

        # Get target
        result = self.execute("target-get")
        expect(result).to_be_like("No target set.")

    def test_can_get_target(self):
        # Get target
        result = self.execute("target-get")
        expect(result).to_be_like("Current target set to '%s'." % self.target)
