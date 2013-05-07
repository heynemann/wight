#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from json import loads

import sys

from cement.core import controller
from prettytable import PrettyTable
import requests

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
            response = self.api("/teams/%s" % name)
            if response.status_code == 200:
                self.write("")
                self.write(name)
                self.write("=" * len(name))
                self.write("")
                self.write("Team members:")
                team_data = loads(response.content)
                members_table = PrettyTable(["user", "role"])
                members_table.align["user"] = "l"
                members_table.add_row([team_data["owner"], "owner"])
                for member in team_data["members"]:
                    members_table.add_row([member, "member"])
                self.write(members_table)
                self.write("")
            elif response.status_code == 404:
                self.write("The team '%s' does not exists in target '%s'." % (name, target))
