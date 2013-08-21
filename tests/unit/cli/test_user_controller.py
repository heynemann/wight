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
import requests
from wight.models import UserData
from wight.cli.user import ShowUserController, ChangePasswordController
from tests.unit.base import TestCase, ApiTestCase
from preggy import expect


class TestChangePasswordController(ApiTestCase, TestCase):

    @patch.object(requests, 'post')
    @patch.object(ChangePasswordController, 'putsuccess')
    @patch.object(ChangePasswordController, 'get_pass')
    def test_change_password_normally(self, get_pass_mock, putsuccess_mock, post_mock):
        post_mock.return_value = Mock(status_code=200)
        get_pass_mock.return_value = "testing"

        ctrl = self.make_controller(ChangePasswordController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.app.user_data.token = "token-value"
        ctrl.default()

        call_list = get_pass_mock.call_args_list
        expect(str(call_list[0]).split("'")[1]).to_equal("Please enter your \\x1b[35m\\x1b[1mcurrent password\\x1b[0m\\x1b[37m\\x1b[2m:")
        expect(str(call_list[1]).split("'")[1]).to_equal("Please enter your \\x1b[35m\\x1b[1mnew password\\x1b[0m\\x1b[37m\\x1b[2m:")
        expect(str(call_list[2]).split("'")[1]).to_equal("Please enter your \\x1b[35m\\x1b[1mnew password again\\x1b[0m\\x1b[37m\\x1b[2m:")

        putsuccess_mock.assert_called_with("Password changed successfully.")

    @patch.object(requests, 'post')
    @patch.object(ChangePasswordController, 'puterror')
    @patch.object(ChangePasswordController, 'get_pass')
    def test_change_password_fails_if_old_pass_is_wrong(self, get_pass_mock, puterror_mock, post_mock):
        post_mock.return_value = Mock(status_code=403)
        get_pass_mock.return_value = "testing"

        ctrl = self.make_controller(ChangePasswordController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.app.user_data.token = "token-value"
        ctrl.default()

        puterror_mock.assert_called_with("The original password didn't match. Please try again")

    @patch.object(requests, 'post')
    @patch.object(ChangePasswordController, 'puterror')
    @patch.object(ChangePasswordController, 'get_pass')
    def test_change_password_message_if_unknown_return_code_from_api(self, get_pass_mock, puterror_mock, post_mock):
        post_mock.return_value = Mock(status_code=500)
        get_pass_mock.return_value = "testing"

        ctrl = self.make_controller(ChangePasswordController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.app.user_data.token = "token-value"
        ctrl.default()

        puterror_mock.assert_called_with("Wight API returned an unexpected status code!")

    @patch.object(ChangePasswordController, 'puterror')
    @patch.object(ChangePasswordController, 'get_pass')
    def test_change_password_fails_if_password_matching_fails(self, get_pass_mock, puterror_mock):

        ctrl = self.make_controller(ChangePasswordController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.app.user_data.token = "token-value"
        pass_values = ['testing', 'retesting', 'reretesting']
        def side_effect(self):
            return pass_values.pop()
        get_pass_mock.side_effect = side_effect

        ctrl.default()
        puterror_mock.assert_called_with("New password check failed. Please try again.")


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
        write_mock.assert_called_with("You are not authenticated. Try running wight login before using user-info.")

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
