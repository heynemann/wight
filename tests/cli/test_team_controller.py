#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from mock import patch
import requests

from preggy import expect

from wight.cli.team import CreateTeamController
from tests.base import TestCase
from wight.models import UserData


class TestCreateTeamController(TestCase):
    @patch.object(CreateTeamController, 'post')
    def test_create_team(self, post_mock):
        ctrl = self.make_controller(CreateTeamController, conf=self.fixture_for('test.conf'), team_name='nameless')
        ctrl.app.user_data = UserData(target="Target")
        ctrl.default()
        post_mock.assert_called_with("/teams", {"name": "nameless"})

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_create_team_notify_user(self, write_mock, post_mock):
        ctrl = self.make_controller(CreateTeamController, conf=self.fixture_for('test.conf'), team_name='nameless')
        ctrl.app.user_data = UserData(target="Target")
        ctrl.default()
        write_mock.assert_called_with("Created 'nameless' team in 'Target' target.")

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_create_gets_server_error_and_notify(self, write_mock, post_mock):
        post_mock.side_effect = requests.ConnectionError
        ctrl = self.make_controller(CreateTeamController, conf=self.fixture_for('test.conf'), team_name='nameless')
        ctrl.app.user_data = UserData(target="Target")
        ctrl.default()
        write_mock.assert_called_with("The server did not respond. Check your connection with the target 'Target'.")
