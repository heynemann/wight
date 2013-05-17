#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from datetime import datetime
from json import dumps
from uuid import uuid4

from wight.errors import UnauthenticatedError

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from mock import patch, Mock, call

from preggy import expect

from wight.cli.load_test import ScheduleLoadTestController, ListLoadTestController

from wight.models import UserData
from wight.cli.base import requests
from tests.unit.base import TestCase


def get_mock_side_effect(*args, **kwargs):
    if args[0] == "/user/info":
        return """
        {
            "user": {
                "email": "awesome@gmail.com",
                "teams": [
                    {"name": "team1", "role": "owner"},
                    {"name": "team2", "role": "member"}
                ]
            }
        }
        """
    elif args[0] == "/teams/team1":
        return """
        {
            "projects": [
                {"name": "project1"},
                {"name": "project2"}
            ]
        }
        """
    elif args[0] == "/teams/team2":
        return """
        {
            "projects": [
                {"name": "project3"},
                {"name": "project4"}
            ]
        }
        """
    elif args[0] == "/teams/nameless":
        return """
        {
            "projects": [
                {"name": "project-nameless1"},
                {"name": "project-nameless2"}
            ]
        }
        """
    elif args[0] == "/teams/nameless/projects/project-nameless1/load_tests/":
        return generate_fake_load_you_know_what(2, "nameless", "project-nameless1")
    elif args[0] == "/teams/nameless/projects/project-nameless2/load_tests/":
        return generate_fake_load_you_know_what(1, "nameless", "project-nameless2")
    elif args[0] == "/teams/team1/projects/project1/load_tests/":
        return generate_fake_load_you_know_what(1, "team1", "project1")
    elif args[0] == "/teams/team1/projects/project2/load_tests/":
        return generate_fake_load_you_know_what(1, "team1", "project1")
    elif args[0] == "/teams/team2/projects/project3/load_tests/":
        return generate_fake_load_you_know_what(3, "team1", "project1")
    elif args[0] == "/teams/team2/projects/project4/load_tests/":
        return generate_fake_load_you_know_what(1, "team1", "project1")
    elif args[0] == "/teams/nameless/projects/project-nany/load_tests/":
        return generate_fake_load_you_know_what(1, "nameless", "project-nany")

    return ""


def generate_fake_load_you_know_what(quantity, team, project):
    load_tests = []
    for i in range(quantity):
        load_tests.append({
            "baseUrl": "http://some-server.com/some-url",
            "uuid": "um-uuid-legal",
            "createdBy": "",
            "team": team,
            "project": project,
            "scheduled": True,
            "created": "31/12/2060 00:00:00",
            "lastModified": "31/12/2060 00:00:00",
        })
    return dumps(load_tests)


class LoadTestControllerTestBase(TestCase):
    def setUp(self):
        self.ctrl = self.make_controller(self.controller_class, conf=self.fixture_for('test.conf'), **self.controller_kwargs)
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"
        self.get_mock = patch('requests.get')
        self.get_mock.start()

    def tearDown(self):
        self.get_mock.stop()


class LoadTestControllerTest(LoadTestControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": "nameless", "project_name": "project", "base_url": "http://www.globo.com"}
        self.controller_class = ScheduleLoadTestController
        super(LoadTestControllerTest, self).setUp()

    @patch.object(ScheduleLoadTestController, 'post')
    def test_schedule_test(self, post_mock):
        self.ctrl.default()
        post_mock.assert_any_call("/teams/nameless/projects/project/load_tests/", {
            "base_url": "http://www.globo.com"
        })

    @patch.object(ScheduleLoadTestController, 'post')
    @patch.object(ScheduleLoadTestController, 'write')
    def test_schedule_test_notifies_user(self, write_mock, post_mock):
        response = Mock(status_code=200)
        post_mock.return_value = response
        self.ctrl.default()
        msg = "Scheduled a new load test for project 'project' in team 'nameless' at 'Target' target."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(ScheduleLoadTestController, 'post')
    @patch.object(ScheduleLoadTestController, 'write')
    def test_schedule_gets_server_error_and_notify(self, write_mock, post_mock):
        post_mock.side_effect = requests.ConnectionError
        self.ctrl.default()
        msg = "The server did not respond. Check your connection with the target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(ScheduleLoadTestController, 'post')
    @patch.object(ScheduleLoadTestController, 'write')
    def test_schedule_test_when_project_not_found(self, write_mock, post_mock):
        response = Mock(status_code=404)
        post_mock.return_value = response
        self.ctrl.default()
        msg = "Project or team not found at target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)


class ListAllLoadTestControllerTest(LoadTestControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": None, "project_name": None}
        self.controller_class = ListLoadTestController
        super(ListAllLoadTestControllerTest, self).setUp()

    def test_not_work_if_not_authenticated(self):
        self.ctrl.app.user_data.token = None
        try:
            self.ctrl.default()
        except UnauthenticatedError:
            assert True
            return

        assert False, "Should not have gotten this far"

    @patch.object(ListLoadTestController, 'get')
    def test_get_user_info_to_use_team_as_filter(self, get_mock):
        get_mock.side_effect = get_mock_side_effect
        self.ctrl.default()
        get_mock.assert_any_call("/user/info")

    @patch.object(ListLoadTestController, 'get')
    def test_get_all_teams_for_user_and_get_info_for_it(self, get_mock):
        get_mock.side_effect = get_mock_side_effect
        self.ctrl.default()
        get_mock.assert_any_call("/user/info")
        get_mock.assert_any_call("/teams/team1")
        get_mock.assert_any_call("/teams/team2")

    @patch.object(ListLoadTestController, 'get')
    def test_get_load_tests_for_team_and_project(self, get_mock):
        get_mock.side_effect = get_mock_side_effect
        self.ctrl.default()
        get_mock.assert_any_call("/teams/team1/projects/project1/load_tests/")
        get_mock.assert_any_call("/teams/team1/projects/project2/load_tests/")
        get_mock.assert_any_call("/teams/team2/projects/project3/load_tests/")
        get_mock.assert_any_call("/teams/team2/projects/project4/load_tests/")

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(ListLoadTestController, 'get')
    def test_get_show_right_stuff(self, get_mock, mock_stdout):
        get_mock.side_effect = get_mock_side_effect
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            """
                Team: team1 ---- Project: project1
                +---------------+--------+--------------------------+
                | uuid          | status |                          |
                +---------------+--------+--------------------------+
                | um-uuid-legal |  True  | wight show um-uuid-legal |
                +---------------+--------+--------------------------+

                Team: team1 ---- Project: project2
                +---------------+--------+--------------------------+
                | uuid          | status |                          |
                +---------------+--------+--------------------------+
                | um-uuid-legal |  True  | wight show um-uuid-legal |
                +---------------+--------+--------------------------+

                Team: team2 ---- Project: project3
                +---------------+--------+--------------------------+
                | uuid          | status |                          |
                +---------------+--------+--------------------------+
                | um-uuid-legal |  True  | wight show um-uuid-legal |
                | um-uuid-legal |  True  | wight show um-uuid-legal |
                | um-uuid-legal |  True  | wight show um-uuid-legal |
                +---------------+--------+--------------------------+

                Team: team2 ---- Project: project4
                +---------------+--------+--------------------------+
                | uuid          | status |                          |
                +---------------+--------+--------------------------+
                | um-uuid-legal |  True  | wight show um-uuid-legal |
                +---------------+--------+--------------------------+
            """
        )


class ListTeamLoadTestControllerTest(LoadTestControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": "nameless", "project_name": None}
        self.controller_class = ListLoadTestController
        super(ListTeamLoadTestControllerTest, self).setUp()

    @patch.object(ListLoadTestController, 'get')
    def test_dont_get_teams_if_team_name_is_passed(self, get_mock):
        get_mock.side_effect = get_mock_side_effect
        self.ctrl.default()
        calls = get_mock.call_args_list
        expect(calls).not_to_include(call("/user/info"))
        get_mock.assert_any_call("/teams/nameless")
        get_mock.assert_any_call("/teams/nameless/projects/project-nameless1/load_tests/")
        get_mock.assert_any_call("/teams/nameless/projects/project-nameless2/load_tests/")


class ListTeamAndProjectLoadTestControllerTest(LoadTestControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": "nameless", "project_name": "project-nany"}
        self.controller_class = ListLoadTestController
        super(ListTeamAndProjectLoadTestControllerTest, self).setUp()

    @patch.object(ListLoadTestController, 'get')
    def test_dont_get_dont_load_projects_names(self, get_mock):
        get_mock.side_effect = get_mock_side_effect
        self.ctrl.default()
        calls = get_mock.call_args_list
        expect(calls).not_to_include(call("/user/info"))
        expect(calls).not_to_include(call("/teams/nameless/projects/project-nameless1/load_tests/"))
        expect(calls).not_to_include(call("/teams/nameless/projects/project-nameless2/load_tests/"))
        get_mock.assert_any_call("/teams/nameless")
        get_mock.assert_any_call("/teams/nameless/projects/project-nany/load_tests/")
