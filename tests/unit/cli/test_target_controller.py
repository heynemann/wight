#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import mock
from preggy import expect

from wight.models import UserData
from wight.cli.target import TargetSetController, TargetGetController
from tests.unit.base import TestCase


class TestTargetSetController(TestCase):
    def test_set_target(self):
        ctrl = self.make_controller(TargetSetController, conf=self.fixture_for('test.conf'), target='http://my-target.wight.com')
        ctrl.default()

        ud = UserData.load()
        expect(ud).not_to_be_null()
        expect(ud.target).to_equal("http://my-target.wight.com")


class TestTargetGetController(TestCase):
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_get_target(self, mock_stdout):
        set_ctrl = self.make_controller(TargetSetController, conf=self.fixture_for('test.conf'), target='http://my-target.wight.com')
        set_ctrl.default()

        ctrl = self.make_controller(TargetGetController, conf=self.fixture_for('test.conf'))
        ctrl.default()
        expect(mock_stdout.getvalue()).to_include("Current target set to 'http://my-target.wight.com'.")

    @mock.patch.object(TargetGetController, 'write')
    @mock.patch.object(UserData, 'load')
    def test_get_target_without_user_data(self, load_mock, write_mock):
        load_mock.return_value = None
        ctrl = self.make_controller(TargetGetController, conf=self.fixture_for('test.conf'))
        ctrl.default()
        write_mock.assert_called_with("No target set.")
