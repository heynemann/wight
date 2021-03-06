#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import os
from os.path import exists
import re
import sys
from six import binary_type

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from preggy import expect
import mock

from wight.cli.app import WightApp
from wight.cli.auth import AuthController
from wight.models import UserData
from tests.unit.base import FullTestCase
from tests.factories import UserFactory


def clear_token():
    if exists(UserData.DEFAULT_PATH):
        os.remove(UserData.DEFAULT_PATH)


def assert_token_is(token):
    data = UserData.load()
    expect(data.token).to_equal(token)


REMOVE_COLORS_REGEX = re.compile(
    r'(\033|\x1b|\x03)'  # prefixes
    r'\['                # non-regex bracket
    r'([0-9]*[;])?'      # semi-colon
    r'[0-9]*m',          # suffix
    flags=re.UNICODE
)

NORMALIZE_WHITESPACE_REGEX = re.compile(
    r'\s+',
    flags=re.UNICODE|re.MULTILINE|re.IGNORECASE
)

_filter_str = lambda s: NORMALIZE_WHITESPACE_REGEX.sub('', s.lower()).strip()


def strip_string(text):
    if isinstance(text, (binary_type, )):
        text = text.decode('utf-8')
    text = REMOVE_COLORS_REGEX.sub('', text)
    text = _filter_str(text)
    if isinstance(text, (binary_type, )):
        text = text.decode('utf-8')
    return text


class AuthControllerTestCase(FullTestCase):
    def setUp(self, *args, **kw):
        super(AuthControllerTestCase, self).setUp(*args, **kw)
        clear_token()
        self.get_mock = mock.patch('requests.get')
        self.get_mock.start()

    def test_meta(self):
        meta = AuthController.Meta
        expect(meta.label).to_equal('login')
        expect(meta.description).to_equal('Log-in to wight (or register if user not found).')
        expect(meta.config_defaults).to_be_empty()

        expect(meta.arguments).to_be_like([
            (['email'], dict(help='E-mail to authenticate with.')),
            (['--password'], dict(help='Password to authenticate with.', required=False)),
        ])

    @mock.patch.object(AuthController, 'write')
    def test_default_action_when_target_not_set(self, write_mock):
        self.expected = ""

        def assert_written(message):
            if message.strip() != "":
                self.expected = message

        write_mock.side_effect = assert_written

        wightApp = WightApp()
        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), app=wightApp)

        try:
            expect(ctrl.default()).to_be_false()
            assert False, "Should have called sys.exit(0)"
        except SystemExit:
            assert True

        expected = "You need to set the target to use wight. Use 'wight target-set <url of target>' to login."
        expect(self.expected).to_be_like(expected)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(AuthController, 'ask_for')
    def test_default_action_when_email_is_none(self, ask_for_mock, mock_stdout):
        ask_for_mock.return_value = None

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=None)
        ctrl.app.user_data = UserData(target="test-target")

        expect(ctrl.default()).to_be_false()

        expect(mock_stdout.getvalue()).to_be_like("Aborting...")
        expect(ask_for_mock.called).to_be_true()

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(AuthController, 'get_pass')
    @mock.patch.object(AuthController, 'ask_for')
    def test_default_action_when_pwd_is_none(self, ask_for_mock, get_pass_mock, mock_stdout):
        ask_for_mock.return_value = "test@test.com"
        get_pass_mock.return_value = None

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=None, password=None)
        ctrl.app.user_data = UserData(target="test-target")

        expect(ctrl.default()).to_be_false()

        expect(mock_stdout.getvalue()).to_be_like("Aborting...")
        expect(ask_for_mock.called).to_be_true()
        expect(get_pass_mock.called).to_be_true()

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(AuthController, 'get')
    def test_default_action_when_invalid_password(self, get_mock, mock_stdout):
        user = UserFactory.create()

        response_mock = mock.Mock(status_code=403)
        get_mock.return_value = response_mock

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=user.email, password="123")
        ctrl.app.user_data = UserData(target=self.get_url('/'))
        expect(ctrl.default()).to_be_false()

        expect(mock_stdout.getvalue()).to_be_like("Authentication failed.")
        expect(get_mock.called).to_be_true()

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(AuthController, 'ask_for')
    @mock.patch.object(AuthController, 'get')
    def test_default_action_when_user_not_found_but_dont_want_to_register(self, get_mock, ask_for_mock, mock_stdout):
        user = UserFactory.create()

        response_mock = mock.Mock(status_code=404)
        get_mock.return_value = response_mock
        ask_for_mock.return_value = "N"

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=user.email, password="123")
        ctrl.app.user_data = UserData(target=self.get_url('/'))
        expect(ctrl.default()).to_be_false()

        expect(mock_stdout.getvalue()).to_be_like("Aborting...")
        expect(get_mock.called).to_be_true()

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(AuthController, '_confirming_password')
    @mock.patch.object(AuthController, 'ask_for')
    @mock.patch.object(AuthController, 'get')
    def test_default_action_when_user_not_found_but_want_to_register(self, get_mock, ask_for_mock, confirm_mock, mock_stdout):
        user = UserFactory.create()

        headers_mock = mock.Mock(get=lambda msg: "test-token")
        response_mock = mock.Mock(status_code=404, headers=headers_mock)
        get_mock.return_value = response_mock
        ask_for_mock.return_value = "Y"
        confirm_mock.return_value = "123"

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=user.email, password="123")
        ctrl.app.user_data = UserData(target=self.get_url('/'))
        expect(ctrl.default()).to_be_true()



        expect(mock_stdout.getvalue()).to_be_like("User registered and authenticated.")
        expect(get_mock.called).to_be_true()

        assert_token_is("test-token")

    def get_pass_side_correct(self, message):
        if strip_string(message) == strip_string("Please retype the password to confirm:"):
            return "123"
        return "321"

    def get_pass_side_error(self, message):
        if strip_string(message) == strip_string("Confirm not match! Please enter the password again:"):
            return "123"
        if strip_string(message) == strip_string("Please retype the password to confirm:"):
            return "123"
        return "321"

    @mock.patch.object(AuthController, 'get_pass')
    def test_confirm_password_correctly(self, get_pass_mock):
        get_pass_mock.side_effect = self.get_pass_side_correct
        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email="mail", password="123")
        ctrl._confirming_password("123")
        expect(len(get_pass_mock.call_args_list)).to_equal(1)

    @mock.patch.object(AuthController, 'get_pass')
    def test_confirm_password_with_type_error(self, get_pass_mock):
        get_pass_mock.side_effect = self.get_pass_side_error
        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email="mail", password="123")
        ctrl._confirming_password("321")
        expect(len(get_pass_mock.call_args_list)).to_equal(3)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(AuthController, 'get')
    def test_default_action_when_user_authenticated_properly(self, get_mock, mock_stdout):
        user = UserFactory.create()

        headers_mock = mock.Mock(get=lambda msg: "test-token-2")
        response_mock = mock.Mock(status_code=200, headers=headers_mock)
        get_mock.return_value = response_mock

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=user.email, password=UserFactory.get_default_password())
        ctrl.app.user_data = UserData(target=self.get_url('/'))
        expect(ctrl.default()).to_be_true()

        expect(mock_stdout.getvalue()).to_be_like("Authenticated.")
        expect(get_mock.called).to_be_true()

        assert_token_is("test-token-2")
