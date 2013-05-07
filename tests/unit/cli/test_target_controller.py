#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import UserData
from wight.cli.target import TargetSetController
from tests.unit.base import TestCase


class TestTargetSetController(TestCase):
    def test_set_target(self):
        ctrl = self.make_controller(TargetSetController, conf=self.fixture_for('test.conf'), target='http://my-target.wight.com')
        ctrl.default()

        ud = UserData.load()
        expect(ud).not_to_be_null()
        expect(ud.target).to_equal("http://my-target.wight.com")
