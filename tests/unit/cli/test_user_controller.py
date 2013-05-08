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

from mock import patch, Mock

from wight.models import UserData
from wight.cli.user import ShowUserController
from tests.unit.base import TestCase
from preggy import expect


class TestShowUserController(TestCase):
    def setUp(self):
        self.ctrl = self.make_controller(ShowUserController, conf=self.fixture_for('test.conf'), team_name='nameless')
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"
        self.get_mock = patch('requests.get')
        self.get_mock.start()

    def tearDown(self):
        self.get_mock.stop()

    @patch.object(ShowUserController, 'get')
    @patch.object(ShowUserController, 'write')
    def test_user_info_shows_not_logged_in_message(self, write_mock, get_mock):
        get_mock.return_value = Mock(status_code=401, content="""
            {
                "user": {"email": "awesome@gmail.com", "teams": []}
            }
        """)

        self.ctrl.default()
        write_mock.assert_called_with("User not logged in. Run wight authenticate")

    @patch.object(ShowUserController, 'get')
    @patch('sys.stdout', new_callable=StringIO)
    def test_user_info_shows_user_email(self, mock_stdout, get_mock):
        get_mock.return_value = Mock(status_code=200, content="""
            {
                "user": {"email": "awesome@gmail.com", "teams": [{"name": "team1", "role": "owner"}]}
            }
        """)

        self.ctrl.default()
        expected_stdout = """
            User: awesome@gmail.com

            +-------+-------+
            | team  | role  |
            +-------+-------+
            | team1 | owner |
            +-------+-------+
        """
        expect(mock_stdout.getvalue()).to_be_like(expected_stdout)
