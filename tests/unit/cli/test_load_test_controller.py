#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from wight.errors import UnauthenticatedError

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from mock import patch, Mock

from preggy import expect

from wight.cli.load_test import ScheduleLoadTestController

from wight.models import UserData
from wight.cli.base import requests
from tests.unit.base import TestCase


class LoadTestControllerTestBase(TestCase):
    def setUp(self):
        self.ctrl = self.make_controller(self.controller_class, conf=self.fixture_for('test.conf'), **self.controller_kwargs)
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"
        self.get_mock = patch('requests.get')
        self.get_mock.start()

    def tearDown(self):
        self.get_mock.stop()


class LoadTestControllerTest(LoadTestControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": "nameless", "project_name": "project", "base_url": "http://www.globo.com"}
        self.controller_class = ScheduleLoadTestController
        super(LoadTestControllerTest, self).setUp()

    @patch.object(ScheduleLoadTestController, 'post')
    def test_schedule_test(self, post_mock):
        self.ctrl.default()
        post_mock.assert_any_call("/teams/nameless/projects/project/load_tests/", {
            "base_url": "http://www.globo.com"
        })

    @patch.object(ScheduleLoadTestController, 'post')
    @patch.object(ScheduleLoadTestController, 'write')
    def test_schedule_test_notifies_user(self, write_mock, post_mock):
        response = Mock(status_code=200)
        post_mock.return_value = response
        self.ctrl.default()
        msg = "Scheduled a new load test for project 'project' in team 'nameless' at 'Target' target."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(ScheduleLoadTestController, 'post')
    @patch.object(ScheduleLoadTestController, 'write')
    def test_schedule_gets_server_error_and_notify(self, write_mock, post_mock):
        post_mock.side_effect = requests.ConnectionError
        self.ctrl.default()
        msg = "The server did not respond. Check your connection with the target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(ScheduleLoadTestController, 'post')
    @patch.object(ScheduleLoadTestController, 'write')
    def test_schedule_test_when_project_not_found(self, write_mock, post_mock):
        response = Mock(status_code=404)
        post_mock.return_value = response
        self.ctrl.default()
        msg = "Project or team not found at target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)
