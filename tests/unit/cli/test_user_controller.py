#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com


from mock import patch

from wight.models import UserData
from wight.cli.user import ShowUserController
from tests.unit.base import TestCase


class FakeResponse():
    def __init__(self, status_code, send_connection_error=False):
        self.send_connection_error = send_connection_error
        self.status_code = status_code
        self.content = """
            {
                "user": {"email": "awesome@gmail.com"}
            }
        """


class TestShowUserController(TestCase):
    def setUp(self):
        self.ctrl = self.make_controller(ShowUserController, conf=self.fixture_for('test.conf'), team_name='nameless')
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"
        self.get_mock = patch('requests.get')
        self.get_mock.start()

    def tearDown(self):
        self.get_mock.stop()

    @patch.object(ShowUserController, 'api')
    @patch.object(ShowUserController, 'write')
    def test_user_info_shows_not_logged_in_message(self, write_mock, api_mock):
        api_mock.return_value = FakeResponse(401)

        self.ctrl.default()
        write_mock.assert_called_with("User not logged in. Run wight authenticate")

    @patch.object(ShowUserController, 'api')
    @patch.object(ShowUserController, 'write')
    def test_user_info_shows_user_email(self, write_mock, api_mock):
        api_mock.return_value = FakeResponse(200)

        self.ctrl.default()
        write_mock.assert_called_with("User: awesome@gmail.com")
