#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from os.path import expanduser

from cement.core import controller

from wight.cli.base import WightBaseController
from wight.models import UserData


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
    def default(self):
        self.load_conf()
        user_data = UserData.load(expanduser("~/.wight"))
        name = self.arguments.team_name
        self.write("Created '%s' team in '%s' target." % (name, user_data.target))
        self.post("/teams", {"name": name})
