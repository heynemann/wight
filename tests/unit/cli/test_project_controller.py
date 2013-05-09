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

from mock import patch, Mock
from preggy import expect
import six

from wight.cli.project import CreateProjectController
from wight.cli.base import requests
from wight.models import UserData
from tests.unit.base import TestCase
from tests.factories import TeamFactory


class ProjectControllerTestBase(TestCase):
    def setUp(self):
        self.ctrl = self.make_controller(self.controller_class, conf=self.fixture_for('test.conf'), **self.controller_kwargs)
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"


class TestCreateProjectController(ProjectControllerTestBase):
    def setUp(self):
        if not hasattr(self, 'project_id'):
            self.project_id = 0
        self.project_id += 1

        self.team = TeamFactory.create()
        self.controller_kwargs = {"team": self.team.name, "project_name": "project-%d" % self.project_id, "repo": "repo"}
        self.controller_class = CreateProjectController
        super(TestCreateProjectController, self).setUp()

    def test_create_doesnt_work_if_not_authenticated(self):
        self.ctrl.app.user_data.token = None
        try:
            self.ctrl.default()
        except UnauthenticatedError:
            assert True
            return

        assert False, "Should not have gotten this far"

    @patch.object(CreateProjectController, 'post')
    def test_create_project(self, post_mock):
        self.ctrl.default()
        post_mock.assert_called_with('/teams/%s/projects/' % self.controller_kwargs['team'], {'name': self.controller_kwargs['project_name'], 'repository': self.controller_kwargs['repo']})

    @patch.object(CreateProjectController, 'post')
    @patch.object(CreateProjectController, 'write')
    def test_create_project_notify_user(self, write_mock, post_mock):
        response = Mock(status_code=200)
        post_mock.return_value = response
        self.ctrl.default()
        write_mock.assert_called_with("Created '%s' project in '%s' team at 'Target'." % (self.controller_kwargs['project_name'], self.controller_kwargs['team']))

    @patch.object(CreateProjectController, 'post')
    @patch.object(CreateProjectController, 'write')
    def test_create_gets_server_error_and_notify(self, write_mock, post_mock):
        post_mock.side_effect = requests.ConnectionError
        self.ctrl.default()
        msg = "The server did not respond. Check your connection with the target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(CreateProjectController, 'post')
    @patch.object(CreateProjectController, 'write')
    def test_try_to_create_a_project_that_already_exists(self, write_mock, post_mock):
        response = Mock(status_code=409)
        post_mock.return_value = response
        self.ctrl.default()
        write_mock.assert_called_with("The project '%s' already exists in team '%s' at 'Target'." % (self.controller_kwargs['project_name'], self.controller_kwargs['team']))

    @patch.object(CreateProjectController, 'post')
    @patch.object(CreateProjectController, 'write')
    def test_try_to_create_a_team_with_invalid_arguments(self, write_mock, post_mock):
        response = Mock(status_code=400)
        post_mock.return_value = response
        self.ctrl.default()
        write_mock.assert_called_with("Both name and repository are required in order to save a team.")
