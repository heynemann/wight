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

    def test_set_target_can_complete_with_http(self):
        ctrl = self.make_controller(TargetSetController, conf=self.fixture_for('test.conf'), target='my-target.wight.com')
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
        expected = u"\n\x1b[0m\x1b[32m\x1b[1mWight target set to '\x1b[35m\x1b[1mhttp://my-target.wight.com\x1b[0m\x1b[32m\x1b[1m'. In order to login with wight, use '\x1b[33m\x1b[1mwight login <email>\x1b[0m\x1b[32m\x1b[1m'.\x1b[0m\x1b[32m\x1b[1m\n\n\n\x1b[0m\x1b[32m\x1b[1mCurrent Wight target is '\x1b[35m\x1b[1mhttp://my-target.wight.com\x1b[0m\x1b[32m\x1b[1m'. In order to login with wight, use '\x1b[33m\x1b[1mwight login <email>\x1b[0m\x1b[32m\x1b[1m'.\x1b[0m\x1b[32m\x1b[1m\n\n"
        expect(mock_stdout.getvalue()).to_equal(expected)

    @mock.patch.object(TargetGetController, 'abort')
    @mock.patch.object(UserData, 'load')
    def test_get_target_without_user_data(self, load_mock, abort_mock):
        load_mock.return_value = None
        ctrl = self.make_controller(TargetGetController, conf=self.fixture_for('test.conf'))
        ctrl.default()
        abort_mock.assert_called_with("No target set.")
