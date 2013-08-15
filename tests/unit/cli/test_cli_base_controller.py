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

from preggy import expect
from mock import patch

from wight.cli.base import WightDefaultController, WightBaseController
from wight.models import UserData
from wight.errors import TargetNotSetError, UnauthenticatedError
import wight.cli.base as base

from tests.unit.base import TestCase


class AuthenticatedControllerMock(WightBaseController):
    @WightBaseController.authenticated
    def default(self):
        self.worked = True


class TestBaseController(TestCase):
    @patch.object(base.requests, 'post')
    def test_make_a_post(self, post_mock):
        ctrl = self.make_controller(WightBaseController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.post("/post-url", data={"some": "data"})
        expect(post_mock.called).to_be_true()

    @patch.object(base.requests, 'get')
    def test_make_a_get(self, get_mock):
        ctrl = self.make_controller(WightBaseController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.get("/get-url")
        expect(get_mock.called).to_be_true()

    @patch.object(base.requests, 'put')
    def test_make_a_put(self, put_mock):
        ctrl = self.make_controller(WightBaseController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.put("/put-url", data={"some": "data"})
        expect(put_mock.called).to_be_true()

    @patch.object(base.requests, 'delete')
    def test_make_a_delete(self, delete_mock):
        ctrl = self.make_controller(WightBaseController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.delete("/delete-url/data")
        expect(delete_mock.called).to_be_true()

    @patch.object(base.requests, 'get')
    def test_make_a_get_with_auth(self, get_mock):
        ctrl = self.make_controller(WightBaseController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.app.user_data.token = "Token"
        ctrl.get("/post-url")
        get_mock.assert_called_with("Target/post-url", headers={"X-Wight-Auth": "Token"})

    @patch.object(base.requests, 'post')
    def test_make_a_post_with_correct_values(self, post_mock):
        ctrl = self.make_controller(WightBaseController, conf=self.fixture_for('test.conf'))
        ctrl.app.user_data = UserData(target="Target")
        ctrl.app.user_data.token = "token-value"
        ctrl.post("/post-url", data={"some": "data"})
        post_mock.assert_called_with(
            "Target/post-url",
            data={"some": "data", "target": "Target"},
            headers={"X-Wight-Auth": "token-value"}
        )

    def test_authenticated_decorator_verifies_target(self):
        ctrl = self.make_controller(AuthenticatedControllerMock)
        try:
            ctrl.default()
        except TargetNotSetError:
            assert True
            return

        assert False, "Should not have gotten this far"

    def test_authenticated_decorator_verifies_token_exists(self):
        ctrl = self.make_controller(AuthenticatedControllerMock)
        ctrl.app.user_data = UserData(target="Target")

        try:
            ctrl.default()
        except UnauthenticatedError:
            assert True
            return

        assert False, "Should not have gotten this far"

    def test_authenticated_decorator_works_when_all_values_correct(self):
        ctrl = self.make_controller(AuthenticatedControllerMock)
        ctrl.app.user_data = UserData(target="Target")
        ctrl.app.user_data.token = "token-value"

        ctrl.default()

        expect(ctrl.worked).to_be_true()


class TestDefaultHandler(TestCase):

    def test_meta_label(self):
        expect(WightDefaultController.Meta.label).to_equal('base')

    def test_meta_desc(self):
        expect(WightDefaultController.Meta.description).to_equal('wight load testing scheduler and tracker.')

    @patch('sys.stdout', new_callable=StringIO)
    def test_default_action(self, mock_stdout):
        expected = """
        usage: nosetests [-h] [--debug] [--quiet]

        optional arguments:
        -h, --help  show this help message and exit
        --debug     toggle debug output
        --quiet     suppress all output"""

        ctrl = self.make_controller(WightDefaultController)
        ctrl.default()

        expect(mock_stdout.getvalue()).to_be_like(expected)

    def test_load_conf(self):
        ctrl = self.make_controller(WightDefaultController, conf=self.fixture_for('test.conf'))
        ctrl.load_conf()

        expect(ctrl.config).not_to_be_null()

    def test_load_conf_that_does_not_exist(self):
        ctrl = self.make_controller(WightDefaultController, conf=self.fixture_for('invalid.conf'))
        ctrl.load_conf()

        expect(ctrl.config).not_to_be_null()
