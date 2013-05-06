#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect
import mock

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from wight.cli.auth import AuthController
from wight.models import UserData
from tests.base import FullTestCase


class AuthControllerTestCase(FullTestCase):
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
    def test_default_action_when_email_is_none(self, ask_for_mock, get_pass_mock, mock_stdout):
        ask_for_mock.return_value = "test@test.com"
        get_pass_mock.return_value = None

        ctrl = self.make_controller(AuthController, conf=self.fixture_for('test.conf'), email=None, password=None)
        ctrl.app.user_data = UserData(target="test-target")

        expect(ctrl.default()).to_be_false()

        expect(mock_stdout.getvalue()).to_be_like("Aborting...")
        expect(ask_for_mock.called).to_be_true()
        expect(get_pass_mock.called).to_be_true()
