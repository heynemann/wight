#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import controller


class ScheduleController(controller.CementBaseController):
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
        conf_path = self.app.pargs.conf
        if conf_path is None:
            conf_path = "/etc/wight.conf"

        self.log.info('Using configuration file in %s.' % conf_path)
        self.log.info("Scheduling load test for repository '%s'." % self.app.pargs.repo)
        self.log.info("Type 'wight list' to keep track of your scheduled tests.")
