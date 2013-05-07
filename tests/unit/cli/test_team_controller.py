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

from mock import patch

from preggy import expect

from wight.cli.team import CreateTeamController, ShowTeamController
from wight.models import UserData
from wight.cli.base import requests
from tests.unit.base import TestCase


class FakeResponse():
    def __init__(self, status_code, send_connection_error=False):
        self.send_connection_error = send_connection_error
        self.status_code = status_code
        self.content = """
            {
                "owner": "nameless@owner.com", "name": "nameless",
                "members": ["User 0", "User 1", "User 2"]
            }
        """


class TestCreateTeamController(TestCase):
    def setUp(self):
        self.ctrl = self.make_controller(CreateTeamController, conf=self.fixture_for('test.conf'), team_name='nameless')
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"
        self.get_mock = patch('requests.get')
        self.get_mock.start()

    def tearDown(self):
        self.get_mock.stop()

    def test_create_not_work_if_not_authenticated(self):
        self.ctrl.app.user_data.token = None
        try:
            self.ctrl.default()
        except UnauthenticatedError:
            assert True
            return

        assert False, "Should not have gotten this far"

    @patch.object(CreateTeamController, 'post')
    def test_create_team(self, post_mock):
        self.ctrl.default()
        post_mock.assert_called_with("/teams", {"name": "nameless"})

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_create_team_notify_user(self, write_mock, post_mock):
        post_mock.return_value = FakeResponse(200)
        self.ctrl.default()
        write_mock.assert_called_with("Created 'nameless' team in 'Target' target.")

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_create_gets_server_error_and_notify(self, write_mock, post_mock):
        post_mock.side_effect = requests.ConnectionError
        self.ctrl.default()
        write_mock.assert_called_with("The server did not respond. Check your connection with the target 'Target'.")

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_try_to_create_a_team_already_existed(self, write_mock, post_mock):
        post_mock.return_value = FakeResponse(409)
        self.ctrl.default()
        write_mock.assert_called_with("The team 'nameless' already exists in target 'Target'.")

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_try_to_create_a_team_with_none_as_name(self, write_mock, post_mock):
        post_mock.return_value = FakeResponse(400)
        self.ctrl.default()
        write_mock.assert_called_with("You should define a name for the team to be created.")


class TestShowTeamController(TestCase):
    def setUp(self):
        self.ctrl = self.make_controller(ShowTeamController, conf=self.fixture_for('test.conf'), team_name='nameless')
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"
        self.get_mock = patch('requests.get')
        self.get_mock.start()

    def tearDown(self):
        self.get_mock.stop()

    def test_show_not_work_if_not_authenticated(self):
        self.ctrl.app.user_data.token = None
        try:
            self.ctrl.default()
        except UnauthenticatedError:
            assert True
            return

        assert False, "Should not have gotten this far"

    @patch.object(ShowTeamController, 'api')
    def test_get_team(self, api_mock):
        self.ctrl.default()
        api_mock.assert_called_with("/teams/nameless")

    @patch.object(ShowTeamController, 'api')
    @patch('sys.stdout', new_callable=StringIO)
    def test_create_team_notify_user(self, mock_stdout, api_mock):
        api_mock.return_value = FakeResponse(200)
        self.ctrl.default()
        expected_stdout = """
            nameless
            ========

            Team members:
            +--------------------+--------+
            |        user        |  role  |
            +--------------------+--------+
            | nameless@owner.com | owner  |
            | User 0             | member |
            | User 1             | member |
            | User 2             | member |
            +--------------------+--------+
        """
        expect(mock_stdout.getvalue()).to_be_like(expected_stdout)

    @patch.object(ShowTeamController, 'api')
    @patch.object(ShowTeamController, 'write')
    def test_try_to_create_a_team_already_existed(self, write_mock, api_mock):
        api_mock.return_value = FakeResponse(404)
        self.ctrl.default()
        write_mock.assert_called_with("The team 'nameless' does not exists in target 'Target'.")

    @patch.object(ShowTeamController, 'api')
    @patch.object(ShowTeamController, 'write')
    def test_create_gets_server_error_and_notify(self, write_mock, api_mock):
        api_mock.side_effect = requests.ConnectionError
        self.ctrl.default()
        write_mock.assert_called_with("The server did not respond. Check your connection with the target 'Target'.")