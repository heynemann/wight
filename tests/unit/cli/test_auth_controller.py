#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import os
from os.path import exists

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from preggy import expect
import mock

from wight.cli.app import WightApp
from wight.cli.auth import AuthController
from wight.models import UserData, User
from tests.unit.base import FullTestCase


def clear_token():
    if exists(UserData.DEFAULT_PATH):
        os.remove(UserData.DEFAULT_PATH)


def assert_token_is(token):
    data = UserData.load()
    expect(data.token).to_equal(token)


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
            (['--email'], dict(help='E-mail to authenticate with.', required=False)),
            (['--password'], dict(help='Password to authenticate with.', required=False)),
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
        ])

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_default_action_when_target_not_set(self, mock_stdout):
        wightApp = WightApp()
        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), app=wightApp)

        expect(ctrl.default()).to_be_false()

        expect(mock_stdout.getvalue()).to_be_like("Wight target not set. Please use 'wight target-set <url of target>' to specify the wight api target to be used.")

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
        email = "test1231312@test.com"
        User.create(email=email, password="12345")

        response_mock = mock.Mock(status_code=403)
        get_mock.return_value = response_mock

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=email, password="123")
        ctrl.app.user_data = UserData(target=self.get_url('/'))
        expect(ctrl.default()).to_be_false()

        expect(mock_stdout.getvalue()).to_be_like("Authentication failed.")
        expect(get_mock.called).to_be_true()

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(AuthController, 'ask_for')
    @mock.patch.object(AuthController, 'get')
    def test_default_action_when_user_not_found_but_dont_want_to_register(self, get_mock, ask_for_mock, mock_stdout):
        email = "test1231312@test.com"
        User.create(email=email, password="12345")

        response_mock = mock.Mock(status_code=404)
        get_mock.return_value = response_mock
        ask_for_mock.return_value = "N"

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=email, password="123")
        ctrl.app.user_data = UserData(target=self.get_url('/'))
        expect(ctrl.default()).to_be_false()

        expect(mock_stdout.getvalue()).to_be_like("Aborting...")
        expect(get_mock.called).to_be_true()

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(AuthController, 'ask_for')
    @mock.patch.object(AuthController, 'get')
    def test_default_action_when_user_not_found_but_want_to_register(self, get_mock, ask_for_mock, mock_stdout):
        email = "test1231312@test.com"
        User.create(email=email, password="12345")

        headers_mock = mock.Mock(get=lambda msg: "test-token")
        response_mock = mock.Mock(status_code=404, headers=headers_mock)
        get_mock.return_value = response_mock
        ask_for_mock.return_value = "Y"

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=email, password="123")
        ctrl.app.user_data = UserData(target=self.get_url('/'))
        expect(ctrl.default()).to_be_true()

        expect(mock_stdout.getvalue()).to_be_like("User registered and authenticated.")
        expect(get_mock.called).to_be_true()

        assert_token_is("test-token")

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(AuthController, 'get')
    def test_default_action_when_user_authenticated_properly(self, get_mock, mock_stdout):
        email = "test1231312@test.com"
        User.create(email=email, password="12345")

        headers_mock = mock.Mock(get=lambda msg: "test-token-2")
        response_mock = mock.Mock(status_code=200, headers=headers_mock)
        get_mock.return_value = response_mock

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=email, password="12345")
        ctrl.app.user_data = UserData(target=self.get_url('/'))
        expect(ctrl.default()).to_be_true()

        expect(mock_stdout.getvalue()).to_be_like("Authenticated.")
        expect(get_mock.called).to_be_true()

        assert_token_is("test-token-2")
