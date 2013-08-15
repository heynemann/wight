#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
import mock
from nose.plugins.attrib import attr


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from preggy import expect

from wight.models import UserData
from wight.cli.default import SetDefaultController, GetDefaultController

from tests.unit.base import TestCase


class TestSetDefaultController(TestCase):

    def setUp(self):
        super(TestSetDefaultController, self).setUp()
        self.team = "team-blah"
        self.project = "project-blah"

    def authenticate(self, ctrl):
        ctrl.app.user_data = UserData(target="Target")
        ctrl.app.user_data.token = "token-value"

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_set_team(self, mock_stdout):
        ctrl = self.make_controller(SetDefaultController, conf=self.fixture_for('test.conf'), team=self.team, project=None)
        self.authenticate(ctrl)
        ctrl.default()
        ud = UserData.load()
        expect(hasattr(ud, "team")).to_be_true()
        expect(ud.team).to_equal(self.team)
        expect(hasattr(ud, "project")).to_be_false()
        expect(mock_stdout.getvalue()).to_be_like("Default team set to '%s'. Default project not set." % self.team)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_set_project(self, mock_stdout):
        ctrl = self.make_controller(SetDefaultController, conf=self.fixture_for('test.conf'), team=None, project=self.project)
        self.authenticate(ctrl)
        ctrl.default()
        ud = UserData.load()
        expect(hasattr(ud, "project")).to_be_true()
        expect(ud.project).to_equal(self.project)
        expect(hasattr(ud, "team")).to_be_false()
        expect(mock_stdout.getvalue()).to_be_like("Default team not set. Default project set to '%s'." % self.project)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_set_team_and_project(self, mock_stdout):
        ctrl = self.make_controller(SetDefaultController, conf=self.fixture_for('test.conf'), team=self.team, project=self.project)
        self.authenticate(ctrl)
        ctrl.default()
        ud = UserData.load()
        expect(ud.team).to_equal(self.team)
        expect(ud.project).to_equal(self.project)
        expect(mock_stdout.getvalue()).to_be_like("Default team set to '%s'. Default project set to '%s'." % (self.team, self.project))


class TestGetDefaultController(TestCase):

    def setUp(self):
        super(TestGetDefaultController, self).setUp()
        self.ctrl = self.make_controller(GetDefaultController, conf=self.fixture_for('test.conf'))
        self.authenticate()
        self.team = "team-blah"
        self.project = "project-blah"

    def authenticate(self):
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_get_return_not_set_for_both(self, mock_stdout):
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like("Default team not set. Default project not set.")

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_get_default_team(self, mock_stdout):
        self.ctrl.app.user_data.set_default(team=self.team)
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like("Default team is '%s'. Default project not set." % self.team)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_get_default_project(self, mock_stdout):
        self.ctrl.app.user_data.set_default(project=self.project)
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like("Default team not set. Default project is '%s'." % self.project)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_get_default_team_and_project(self, mock_stdout):
        self.ctrl.app.user_data.set_default(team=self.team, project=self.project)
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like("Default team is '%s'. Default project is '%s'." % (self.team, self.project))
