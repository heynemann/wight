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

from wight.cli.team import CreateTeamController, ShowTeamController,\
    UpdateTeamController, DeleteTeamController,\
    TeamAddUserController, TeamRemoveUserController

from wight.models import UserData
from wight.cli.base import requests
from tests.unit.base import TestCase


class TeamControllerTestBase(TestCase):
    def setUp(self):
        self.ctrl = self.make_controller(self.controller_class, conf=self.fixture_for('test.conf'), **self.controller_kwargs)
        self.ctrl.app.user_data = UserData(target="Target")
        self.ctrl.app.user_data.token = "token-value"
        self.get_mock = patch('requests.get')
        self.get_mock.start()

    def tearDown(self):
        self.get_mock.stop()


class TestCreateTeamController(TeamControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": "nameless"}
        self.controller_class = CreateTeamController
        super(TestCreateTeamController, self).setUp()

    def test_create_not_work_if_not_authenticated(self):
        self.ctrl.app.user_data.token = None
        try:
            self.ctrl.default()
        except UnauthenticatedError:
            assert True
            return

        assert False, "Should not have gotten this far"

    @patch.object(CreateTeamController, 'post')
    def test_create_team(self, post_mock):
        self.ctrl.default()
        post_mock.assert_any_call("/teams", {"name": "nameless"})

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_create_team_notify_user(self, write_mock, post_mock):
        response = Mock(status_code=200)
        post_mock.return_value = response
        self.ctrl.default()
        msg = "Created 'nameless' team in 'Target' target."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_create_gets_server_error_and_notify(self, write_mock, post_mock):
        post_mock.side_effect = requests.ConnectionError
        self.ctrl.default()
        msg = "The server did not respond. Check your connection with the target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_try_to_create_a_team_that_already_exists(self, write_mock, post_mock):
        response = Mock(status_code=409)
        post_mock.return_value = response
        self.ctrl.default()
        msg = "The team 'nameless' already exists in target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(CreateTeamController, 'post')
    @patch.object(CreateTeamController, 'write')
    def test_try_to_create_a_team_with_none_as_name(self, write_mock, post_mock):
        response = Mock(status_code=400)
        post_mock.return_value = response
        self.ctrl.default()
        msg = "You should define a name for the team to be created."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)


class TestShowTeamController(TeamControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": "nameless"}
        self.controller_class = ShowTeamController
        super(TestShowTeamController, self).setUp()

    def test_show_not_work_if_not_authenticated(self):
        self.ctrl.app.user_data.token = None
        try:
            self.ctrl.default()
        except UnauthenticatedError:
            assert True
            return

        assert False, "Should not have gotten this far"

    @patch.object(ShowTeamController, 'get')
    def test_get_team(self, get_mock):
        self.ctrl.default()
        get_mock.assert_any_call("/teams/nameless")

    @patch.object(ShowTeamController, 'get')
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_team_notify_user(self, mock_stdout, get_mock):
        get_mock.return_value = Mock(status_code=200, content="""
            {
                "owner": "nameless@owner.com", "name": "nameless",
                "members": ["User 0", "User 1", "User 2"],
                "projects": [
                    {
                        "name": "project1",
                        "repository": "repository1",
                        "createdBy": "nameless@owner.com"
                    },
                    {
                        "name": "project2",
                        "repository": "repository2",
                        "createdBy": "nameless@owner.com"
                    }
                ]
            }
        """)

        self.ctrl.default()
        expected_stdout = """
        nameless
        --------

        +--------------------+--------+
        | user               | role   |
        +--------------------+--------+
        | nameless@owner.com | owner  |
        | User 0             | member |
        | User 1             | member |
        | User 2             | member |
        +--------------------+--------+


        +--------------+-------------+--------------------+
        | project name | repository  | created by         |
        +--------------+-------------+--------------------+
        | project1     | repository1 | nameless@owner.com |
        | project2     | repository2 | nameless@owner.com |
        +--------------+-------------+--------------------+
        """
        expect(mock_stdout.getvalue()).to_be_like(expected_stdout)

    @patch.object(ShowTeamController, 'get')
    @patch.object(ShowTeamController, 'write')
    def test_try_to_show_a_team_dows_not_exist(self, write_mock, get_mock):
        get_mock.return_value = Mock(status_code=404)
        self.ctrl.default()
        msg = "The team 'nameless' does not exists in target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(ShowTeamController, 'get')
    @patch.object(ShowTeamController, 'write')
    def test_show_gets_server_error_and_notify(self, write_mock, get_mock):
        get_mock.side_effect = requests.ConnectionError

        self.ctrl.default()

        msg = "The server did not respond. Check your connection with the target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)


class TestUpdateTeamController(TeamControllerTestBase):
    def setUp(self):
        self.controller_class = UpdateTeamController
        self.controller_kwargs = {"team_name": 'new-team', "new_name": "new-name"}
        super(TestUpdateTeamController, self).setUp()

    @patch.object(UpdateTeamController, 'put')
    @patch.object(UpdateTeamController, 'write')
    def test_handles_connection_errors_nicely(self, write_mock, put_mock):
        put_mock.side_effect = requests.ConnectionError
        self.ctrl.default()
        msg = "The server did not respond. Check your connection with the target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(UpdateTeamController, 'put')
    @patch.object(UpdateTeamController, 'write')
    def test_handles_not_the_owner(self, write_mock, put_mock):
        response_mock = Mock(status_code=403)
        put_mock.return_value = response_mock

        self.ctrl.default()

        msg = "You are not the owner of team 'new-team' in target 'Target' (which means you can't update it)."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(UpdateTeamController, 'put')
    @patch.object(UpdateTeamController, 'write')
    def test_handles_not_found(self, write_mock, put_mock):
        response_mock = Mock(status_code=404)
        put_mock.return_value = response_mock
        self.ctrl.default()
        msg = "Team 'new-team' does not exist in target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(UpdateTeamController, 'put')
    @patch.object(UpdateTeamController, 'write')
    def test_handles_empty_name(self, write_mock, put_mock):
        response_mock = Mock(status_code=400)
        put_mock.return_value = response_mock
        self.ctrl.default()
        msg = "The team's new name can't be null or empty."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(UpdateTeamController, 'put')
    @patch.object(UpdateTeamController, 'write')
    def test_handles_proper_update(self, write_mock, put_mock):
        response_mock = Mock(status_code=200)
        put_mock.return_value = response_mock

        self.ctrl.default()

        msg = "Updated 'new-team' team to 'new-name' in 'Target' target."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)


class TestDeleteTeamController(TeamControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": "nameless"}
        self.controller_class = DeleteTeamController
        super(TestDeleteTeamController, self).setUp()

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(DeleteTeamController, 'ask_for')
    @patch.object(DeleteTeamController, 'delete')
    def test_should_show_confirm_deletion_message(self, delete_mock, ask_mock, stdout_mock):
        ask_mock.return_value = "nameless"
        self.ctrl.default()
        expect(stdout_mock.getvalue()).to_be_like("This operation will delete all projects and all tests of team 'nameless'. You have to retype the team name to confirm deletion.")
        ask_mock.called_with("Tem name: ")

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(DeleteTeamController, 'ask_for')
    def test_should_return_if_name_not_type_correctly(self, ask_mock, stdout_mock):
        ask_mock.return_value = "namel"
        self.ctrl.default()
        expect(stdout_mock.getvalue()).to_be_like(
            """
                This operation will delete all projects and all tests of team 'nameless'.
                You have to retype the team name to confirm deletion.

                The team name you type ('nameless') is not the same you pass ('namel').
                Operation aborted...
            """
        )

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(DeleteTeamController, 'ask_for')
    @patch.object(DeleteTeamController, 'delete')
    def test_should_make_the_delete_in_api(self, delete_mock, ask_mock, stdout_mock):
        ask_mock.return_value = "nameless"
        delete_mock.return_value = Mock(status_code=200)
        self.ctrl.default()
        delete_mock.assert_any_call("/teams/nameless")
        expect(stdout_mock.getvalue()).to_be_like(
            """
                This operation will delete all projects and all tests of team 'nameless'.
                You have to retype the team name to confirm deletion.

                Deleted 'nameless' team, all its projects and tests in 'Target' target.
            """
        )

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(DeleteTeamController, 'ask_for')
    @patch.object(DeleteTeamController, 'delete')
    def test_should_notify_user_if_status_code_was_forbidden(self, delete_mock, ask_mock, stdout_mock):
        ask_mock.return_value = "nameless"
        delete_mock.return_value = Mock(status_code=403)
        self.ctrl.default()
        delete_mock.assert_any_call("/teams/nameless")
        expect(stdout_mock.getvalue()).to_be_like(
            """
                This operation will delete all projects and all tests of team 'nameless'.
                You have to retype the team name to confirm deletion.

                You are not the owner of team 'nameless' in target 'Target' (which means you can't delete it).
            """
        )

    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(DeleteTeamController, 'ask_for')
    @patch.object(DeleteTeamController, 'delete')
    def test_should_notify_user_if_status_code_was_not_found(self, delete_mock, ask_mock, stdout_mock):
        ask_mock.return_value = "nameless"
        delete_mock.return_value = Mock(status_code=404)
        self.ctrl.default()
        delete_mock.assert_any_call("/teams/nameless")
        expect(stdout_mock.getvalue()).to_be_like(
            """
                This operation will delete all projects and all tests of team 'nameless'.
                You have to retype the team name to confirm deletion.

                Team 'nameless' does not exist in target 'Target'.
            """
        )


class TestAddUserTeamController(TeamControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": "awesome", "user_email": "Ryu@streetFighter.com"}
        self.controller_class = TeamAddUserController
        super(TestAddUserTeamController, self).setUp()

    @patch.object(TeamAddUserController, 'patch')
    @patch.object(TeamAddUserController, 'write')
    def test_add_user_without_user_parameter(self, write_mock, patch_mock):
        response_mock = Mock(status_code=403)
        patch_mock.return_value = response_mock
        self.ctrl.default()

        msg = "You are not authenticated. Please use 'wight login'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(TeamAddUserController, 'patch')
    @patch.object(TeamAddUserController, 'write')
    def test_add_user_to_a_non_existing_team(self, write_mock, patch_mock):
        response_mock = Mock(status_code=404)
        patch_mock.return_value = response_mock
        self.ctrl.default()

        msg = "Team 'awesome' does not exist in target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(TeamAddUserController, 'patch')
    @patch.object(TeamAddUserController, 'write')
    def test_add_user_when_not_owner(self, write_mock, patch_mock):
        response_mock = Mock(status_code=401)
        patch_mock.return_value = response_mock
        self.ctrl.default()

        msg = "You need to be the team owner or member to add users."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(TeamAddUserController, 'patch')
    @patch.object(TeamAddUserController, 'write')
    def test_add_user(self, write_mock, patch_mock):
        response_mock = Mock(status_code=200)
        patch_mock.return_value = response_mock
        self.ctrl.default()
        msg = "User 'Ryu@streetFighter.com' added to Team 'awesome'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(TeamAddUserController, 'patch')
    @patch.object(TeamAddUserController, 'write')
    def test_add_user_twice(self, write_mock, patch_mock):
        response_mock = Mock(status_code=409, content='My amazing response')
        patch_mock.return_value = response_mock
        self.ctrl.default()
        expect(write_mock.call_args_list[1][0][0]).to_be_like("My amazing response")


class TestRemoveUserTeamController(TeamControllerTestBase):
    def setUp(self):
        self.controller_kwargs = {"team_name": "awesome", "user_email": "Ryu@streetFighter.com"}
        self.controller_class = TeamRemoveUserController
        super(TestRemoveUserTeamController, self).setUp()

    @patch.object(TeamRemoveUserController, 'delete')
    @patch.object(TeamRemoveUserController, 'write')
    def test_remove_user_without_user_parameter(self, write_mock, delete_mock):
        response_mock = Mock(status_code=403)
        delete_mock.return_value = response_mock

        self.ctrl.default()

        msg = "You are not authenticated. Please use 'wight login'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(TeamRemoveUserController, 'delete')
    @patch.object(TeamRemoveUserController, 'write')
    def test_remove_user_from_a_non_existing_team(self, write_mock, delete_mock):
        response_mock = Mock(status_code=404)
        delete_mock.return_value = response_mock
        self.ctrl.default()

        msg = "Team 'awesome' does not exist in target 'Target'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(TeamRemoveUserController, 'delete')
    @patch.object(TeamRemoveUserController, 'write')
    def test_remove_user_when_not_owner(self, write_mock, delete_mock):
        response_mock = Mock(status_code=401)
        delete_mock.return_value = response_mock

        self.ctrl.default()

        msg = "You need to be the team owner or member to remove users."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)

    @patch.object(TeamRemoveUserController, 'delete')
    @patch.object(TeamRemoveUserController, 'write')
    def test_remove_user(self, write_mock, delete_mock):
        response_mock = Mock(status_code=200)
        delete_mock.return_value = response_mock
        self.ctrl.default()

        msg = "User 'Ryu@streetFighter.com' removed from Team 'awesome'."
        expect(write_mock.call_args_list[1][0][0]).to_be_like(msg)
