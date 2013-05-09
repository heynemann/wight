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


class CreateProjectController(WightBaseController):
    class Meta:
        label = 'create-project'
        stack_on = 'base'
        description = 'Creates a project.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['--team'], dict(help='Name of the team that owns this project.', required=True)),
            (['--project_name'], dict(help='Name of the project.', required=True)),
            (['--repo'], dict(help='Git repository for this project.', required=True)),
        ]

    @controller.expose(hide=False, aliases=["create-project"], help='Creates a project.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        team_name = self.arguments.team
        name = self.arguments.project_name
        repo = self.arguments.repo

        log_message = "Created '%s' project in '%s' team at '%s'." % (name, team_name, target)
        with ConnectedController(self):
            response = self.post("/teams/%s/projects/" % team_name, {"name": name, "repository": repo})
            if response.status_code == 200:
                self.log.info(log_message)
                self.write(log_message)
            elif response.status_code == 409:
                self.write("The project '%s' already exists in team '%s' at '%s'." % (name, team_name, target))
            elif response.status_code == 400:
                self.write("Both name and repository are required in order to save a team.")
