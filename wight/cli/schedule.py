#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys
from cement.core import controller

from wight.cli.base import WightBaseController


class ScheduleController(WightBaseController):
    class Meta:
        label = 'schedule'
        description = 'Schedules a new load test for the given repository.'
        config_defaults = dict()

        arguments = [
            (['--repo'], dict(help='Repository to run tests from.', required=True)),
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
        ]

    @controller.expose(hide=True, help='Schedules a new load test for the given repository.')
    def default(self):
        self.load_conf()
        self.log.info("Scheduling load test for repository '%s'." % self.arguments.repo)
        self.write("Type 'wight list' to keep track of your scheduled tests.\n")
