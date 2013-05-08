#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from json import loads

import six

from cement.core import controller
from prettytable import PrettyTable

from wight.cli.base import WightBaseController, ConnectedController


class CreateTeamController(WightBaseController):
    class Meta:
        label = 'create-team'
        stack_on = 'base'
        description = 'Create a team.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team to be created')),
        ]

    @controller.expose(hide=False, aliases=["create-team"], help='Create a team.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        log_message = "Created '%s' team in '%s' target." % (name, target)
        with ConnectedController(self):
            response = self.post("/teams", {"name": name})
            if response.status_code == 200:
                self.log.info(log_message)
                self.write(log_message)
            elif response.status_code == 409:
                self.write("The team '%s' already exists in target '%s'." % (name, target))
            elif response.status_code == 400:
                self.write("You should define a name for the team to be created.")


class ShowTeamController(WightBaseController):
    class Meta:
        label = 'show-team'
        stack_on = 'base'
        description = 'Show the registered team information.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team to be showed')),
        ]

    @controller.expose(hide=False, aliases=["show-team"], help='Show the registered team information.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        with ConnectedController(self):
            response = self.get("/teams/%s" % name)
            if response.status_code == 200:
                content = response.content
                self.write("")
                self.write(name)
                self.write("=" * len(name))
                self.write("")
                self.write("Team members:")

                if isinstance(content, six.binary_type):
                    content = content.decode('utf-8')
                team_data = loads(content)

                members_table = PrettyTable(["user", "role"])
                members_table.align["user"] = "l"
                members_table.add_row([team_data["owner"], "owner"])
                for member in team_data["members"]:
                    members_table.add_row([member, "member"])
                self.write(members_table)
                self.write("")
            elif response.status_code == 404:
                self.write("The team '%s' does not exists in target '%s'." % (name, target))


class UpdateTeamController(WightBaseController):
    class Meta:
        label = 'update-team'
        stack_on = 'base'
        description = 'Updates a team.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team')),
            (['new_name'], dict(help='The new name for the team')),
        ]

    @controller.expose(hide=False, aliases=["update-team"], help='Updates a team.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        new_name = self.arguments.new_name
        log_message = "Updated '%s' team to '%s' in '%s' target." % (name, new_name, target)

        with ConnectedController(self):
            response = self.put("/teams/%s" % name, {"name": new_name})
            if response.status_code == 200:
                self.log.info(log_message)
                self.write(log_message)
            elif response.status_code == 403:
                self.write("You are not the owner of team '%s' in target '%s' (which means you can't update it)." % (name, target))
            elif response.status_code == 404:
                self.write("Team '%s' does not exist in target '%s'." % (name, target))
            elif response.status_code == 400:
                self.write("The team's new name can't be null or empty.")


class RemoveTeamController(WightBaseController):
    class Meta:
        label = 'remove-team'
        stack_on = 'base'
        description = 'Remove a team.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team to be removed')),
        ]

    @controller.expose(hide=False, aliases=["remove-team"], help='Remove a team.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        self.write("")
        self.write("This operation will remove all projects and all tests of team '%s'." % name)
        self.write("You have to retype the team name to confirm deletion.")
        self.write("")
        name_confirmation = self.ask_for("Team name: ")
        if name_confirmation != name:
            self.write("The team name you type ('%s') is not the same you pass ('%s')." % (name, name_confirmation))
            self.write("Operation aborted...")
            return
        log_message = "Deleted '%s' team, all its projects and tests in '%s' target." % (name, target)
        with ConnectedController(self):
            response = self.delete("/teams/%s" % name)
            if response.status_code == 200:
                self.log.info(log_message)
                self.write(log_message)
            elif response.status_code == 403:
                self.write("You are not the owner of team '%s' in target '%s' (which means you can't delete it)." % (name, target))
            elif response.status_code == 404:
                self.write("Team '%s' does not exist in target '%s'." % (name, target))


class TeamAddUserController(WightBaseController):
    class Meta:
        label = 'team-adduser'
        stack_on = 'base'
        description = 'Adds user to a team'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team')),
            (['user_email'], dict(help='User to be added')),
        ]

    @controller.expose(hide=False, aliases=["team-adduser"], help='Adds user to a team.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        user_email = self.arguments.user_email

        with ConnectedController(self):
            response = self.patch("/teams/%s/members" % name, {"user": user_email})
            if response.status_code == 200:
                self.write("User '%s' added to Team '%s'." % (user_email, name))
            elif response.status_code == 403:
                self.write("Missing parameter user")
            elif response.status_code == 404:
                self.write("Team '%s' does not exist in target '%s'." % (name, target))
            elif response.status_code == 401:
                self.write("You need to be the team owner to add users")
