#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from uuid import uuid4
import mock

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from mock import patch, Mock
from preggy import expect

from wight.cli.project import CreateProjectController, UpdateProjectController, DeleteProjectController
from wight.cli.base import requests
from wight.models import UserData
from wight.errors import UnauthenticatedError

from tests.unit.base import TestCase
# from tests.factories import TeamFactory


class ProjectControllerTestBase(TestCase):
    def setUp(self):
        self.ctrl = self.make_controller(self.controller_class, conf=self.fixture_for('test.conf'), **self.controller_kwargs)
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"


class TestCreateProjectWithoutTeam(ProjectControllerTestBase):
    def setUp(self):
        self.project = "project-blah"
        self.team = "team-blah"
        self.target = "Target"
        self.controller_kwargs = {"team": None, "project": self.project, "repo": "repo"}
        self.controller_class = CreateProjectController
        super(TestCreateProjectWithoutTeam, self).setUp()

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_must_show_error_message_if_default_team_are_not_set(self, mock_stdout):
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            """
A default team was not set and you do not pass one. You can:
    pass a team using --team parameter
    or set a default team with wight default-set --team <team-name> command
            """)

    @patch.object(CreateProjectController, 'post')
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_should_be_possible_create_project_with_default_team(self, mock_stdout, post_mock):
        response = Mock(status_code=200)
        post_mock.return_value = response
        self.ctrl.app.user_data.set_default(team="team-blah")
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            "Created '%s' project in '%s' team at '%s'." % (self.project, self.team, self.target)
        )


class TestCreateProjectController(ProjectControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team": "team-awesome", "project": str(uuid4()), "repo": "repo"}
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
        post_mock.assert_called_with('/teams/%s/projects/' % self.controller_kwargs['team'], {'name': self.controller_kwargs['project'], 'repository': self.controller_kwargs['repo']})

    @patch.object(CreateProjectController, 'post')
    @patch.object(CreateProjectController, 'write')
    def test_create_project_notify_user(self, write_mock, post_mock):
        response = Mock(status_code=200)
        post_mock.return_value = response
        self.ctrl.default()
        expect(write_mock.call_args_list[1][0][0]).to_be_like(
            "Created '%s' project in '%s' team at 'Target'." % (self.controller_kwargs['project'], self.controller_kwargs['team'])
        )

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
        expect(write_mock.call_args_list[1][0][0]).to_be_like(
            "The project '%s' already exists in team '%s' at 'Target'." % (self.controller_kwargs['project'], self.controller_kwargs['team'])
        )

    @patch.object(CreateProjectController, 'post')
    @patch.object(CreateProjectController, 'write')
    def test_try_to_create_a_project_with_invalid_arguments(self, write_mock, post_mock):
        response = Mock(status_code=400)
        post_mock.return_value = response
        self.ctrl.default()
        expect(write_mock.call_args_list[1][0][0]).to_be_like(
            "Both name and repository are required in order to save a team."
        )


class TestUpdateProjectController(ProjectControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {
            "team": "team-awesome",
            "project": "project-awesome",
            "project_name": "new name",
            "repo": "repo"
        }
        self.controller_class = UpdateProjectController
        super(TestUpdateProjectController, self).setUp()

    def test_create_doesnt_work_if_not_authenticated(self):
        self.ctrl.app.user_data.token = None
        try:
            self.ctrl.default()
        except UnauthenticatedError:
            assert True
            return

        assert False, "Should not have gotten this far"

    @patch.object(UpdateProjectController, 'put')
    @patch.object(UpdateProjectController, 'write')
    def test_handles_not_found(self, write_mock, put_mock):
        response_mock = Mock(status_code=404)
        put_mock.return_value = response_mock
        self.ctrl.default()
        msg = "The team '%s' or the project '%s' does not exists in target '%s'." % ("team-awesome", "project-awesome", self.ctrl.app.user_data.target)
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(UpdateProjectController, 'put')
    @patch.object(UpdateProjectController, 'write')
    def test_update_gets_server_error_and_notify(self, write_mock, put_mock):
        put_mock.side_effect = requests.ConnectionError
        self.ctrl.default()
        msg = "The server did not respond. Check your connection with the target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(UpdateProjectController, 'put')
    @patch.object(UpdateProjectController, 'write')
    def test_handle_not_team_member(self, write_mock, put_mock):
        response_mock = Mock(status_code=403)
        put_mock.return_value = response_mock
        self.ctrl.default()
        msg = "You are not member of the team for the project 'project-awesome' and cannot update it."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(UpdateProjectController, 'put')
    def test_update_project(self, put_mock):
        self.ctrl.default()
        put_mock.assert_called_with(
            '/teams/%s/projects/%s' % ("team-awesome", "project-awesome"),
            {'name': "new name", 'repository': "repo"}
        )

    @patch.object(UpdateProjectController, 'put')
    @patch.object(UpdateProjectController, 'write')
    def test_update_project_notify_user(self, write_mock, put_mock):
        response = Mock(status_code=200)
        put_mock.return_value = response
        self.ctrl.default()
        msg = "Updated 'new name' project in 'team-awesome' team at 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)


class TestUpdateProjectWithoutTeam(ProjectControllerTestBase):
    def setUp(self):
        self.project = "project-blah"
        self.team = "team-blah"
        self.target = "Target"
        self.controller_kwargs = {"team": None, "project": self.project, "project_name": "new name", "repo": "repo"}
        self.controller_class = UpdateProjectController
        super(TestUpdateProjectWithoutTeam, self).setUp()

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_must_show_error_message_if_default_team_are_not_set(self, mock_stdout):
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            """
A default team was not set and you do not pass one. You can:
    pass a team using --team parameter
    or set a default team with wight default-set --team <team-name> command
            """)

    @patch.object(UpdateProjectController, 'put')
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_should_be_possible_create_project_with_default_team(self, mock_stdout, put_mock):
        response = Mock(status_code=200)
        put_mock.return_value = response
        self.ctrl.app.user_data.set_default(team=self.team)
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            "Updated 'new name' project in '%s' team at '%s'." % (self.team, self.target)
        )


class TestUpdateProjectWithoutProject(ProjectControllerTestBase):
    def setUp(self):
        self.project = "project-blah"
        self.team = "team-blah"
        self.target = "Target"
        self.controller_kwargs = {"team": self.team, "project": None, "project_name": "new name", "repo": "repo"}
        self.controller_class = UpdateProjectController
        super(TestUpdateProjectWithoutProject, self).setUp()

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_must_show_error_message_if_default_team_are_not_set(self, mock_stdout):
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            """
A default project was not set and you do not pass one. You can:
    pass a project using --project parameter
    or set a default project with wight default-set --project <project-name> command
            """)

    @patch.object(UpdateProjectController, 'put')
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_should_be_possible_create_project_with_default_team(self, mock_stdout, put_mock):
        response = Mock(status_code=200)
        put_mock.return_value = response
        self.ctrl.app.user_data.set_default(project=self.project)
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            "Updated 'new name' project in '%s' team at '%s'." % (self.team, self.target)
        )


class TestUpdateProjectWithoutTeamAndProject(ProjectControllerTestBase):
    def setUp(self):
        self.project = "project-blah"
        self.team = "team-blah"
        self.target = "Target"
        self.controller_kwargs = {"team": None, "project": None, "project_name": "new name", "repo": "repo"}
        self.controller_class = UpdateProjectController
        super(TestUpdateProjectWithoutTeamAndProject, self).setUp()

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_must_show_error_message_if_default_team_are_not_set(self, mock_stdout):
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            """
A default team was not set and you do not pass one. You can:
    pass a team using --team parameter
    or set a default team with wight default-set --team <team-name> command
A default project was not set and you do not pass one. You can:
    pass a project using --project parameter
    or set a default project with wight default-set --project <project-name> command
            """)

    @patch.object(UpdateProjectController, 'put')
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_should_be_possible_create_project_with_default_team(self, mock_stdout, put_mock):
        response = Mock(status_code=200)
        put_mock.return_value = response
        self.ctrl.app.user_data.set_default(team=self.team, project=self.project)
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            "Updated 'new name' project in '%s' team at '%s'." % (self.team, self.target)
        )


class TestDeleteProjectController(ProjectControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {
            "team": "team-awesome",
            "project": "project-awesome",
        }
        self.controller_class = DeleteProjectController
        super(TestDeleteProjectController, self).setUp()

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(DeleteProjectController, 'ask_for')
    @patch.object(DeleteProjectController, 'delete')
    def test_should_show_confirm_deletion_message(self, delete_mock, ask_mock, stdout_mock):
        ask_mock.return_value = "y"
        self.ctrl.default()
        expect(stdout_mock.getvalue()).to_be_like(
            """
            This operation will delete the project 'project-awesome' and all its tests.
            """
        )
        ask_mock.called_with("Are you sure you want to delete project 'project-awesome'? [y/n]")

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(DeleteProjectController, 'ask_for')
    def test_should_return_if_confirmation_not_type_correctly(self, ask_mock, stdout_mock):
        ask_mock.return_value = "n"
        self.ctrl.default()
        expect(stdout_mock.getvalue()).to_be_like(
            """
            This operation will delete the project 'project-awesome' and all its tests.
            Aborting...
            """
        )

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(DeleteProjectController, 'ask_for')
    @patch.object(DeleteProjectController, 'delete')
    def test_should_make_the_delete_in_api(self, delete_mock, ask_mock, stdout_mock):
        ask_mock.return_value = "y"
        delete_mock.return_value = Mock(status_code=200)
        self.ctrl.default()
        delete_mock.assert_any_call("/teams/%s/projects/%s" % ("team-awesome", "project-awesome"))
        expect(stdout_mock.getvalue()).to_be_like(
            """
            This operation will delete the project '%s' and all its tests.
            Deleted '%s' project and tests for team '%s' in 'Target' target.
            """ % ("project-awesome", "project-awesome", "team-awesome")
        )

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(DeleteProjectController, 'ask_for')
    @patch.object(DeleteProjectController, 'delete')
    def test_should_notify_user_if_status_code_was_forbidden(self, delete_mock, ask_mock, stdout_mock):
        ask_mock.return_value = "y"
        delete_mock.return_value = Mock(status_code=403)
        self.ctrl.default()
        delete_mock.assert_any_call("/teams/%s/projects/%s" % ("team-awesome", "project-awesome"))
        expect(stdout_mock.getvalue()).to_be_like(
            """
            This operation will delete the project 'project-awesome' and all its tests.
            You are not member of the team for the project 'project-awesome' and cannot delete it.
            """
        )


class TestDeleteProjectWithoutTeam(ProjectControllerTestBase):
    def setUp(self):
        self.project = "project-blah"
        self.team = "team-blah"
        self.target = "Target"
        self.controller_kwargs = {"team": None, "project": self.project, "project_name": "new name", "repo": "repo"}
        self.controller_class = DeleteProjectController
        super(TestDeleteProjectWithoutTeam, self).setUp()

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_must_show_error_message_if_default_team_are_not_set(self, mock_stdout):
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like(
            """
A default team was not set and you do not pass one. You can:
    pass a team using --team parameter
    or set a default team with wight default-set --team <team-name> command
            """)

    @patch.object(DeleteProjectController, 'ask_for')
    @patch.object(DeleteProjectController, 'delete')
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_should_be_possible_create_project_with_default_team(self, mock_stdout, delete_mock, ask_mock):
        ask_mock.return_value = "y"
        response = Mock(status_code=200)
        delete_mock.return_value = response
        self.ctrl.app.user_data.set_default(team=self.team)
        self.ctrl.default()
        expect(mock_stdout.getvalue()).to_be_like("""
            This operation will delete the project '%s' and all its tests.
            Deleted '%s' project and tests for team '%s' in '%s' target.
        """ % (self.project, self.project, self.team, self.target))
