#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys

from cement.core import controller
import requests

from wight.cli.base import WightBaseController


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
        target = self.app.user_data.target
        name = self.arguments.team_name
        log_message = "Created '%s' team in '%s' target." % (name, target)
        try:
            self.post("/teams", {"name": name})
            self.log.info(log_message)
            self.write(log_message)
        except requests.ConnectionError:
            ex = sys.exc_info()[1]
            self.log.error(ex)
            self.write("The server did not respond. Check your connection with the target '%s'." % target)
