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
        #stacked_on = 'base'
        description = 'Schedules a new load test for the given repository.'
        config_defaults = dict()

        arguments = [
            (['--repo'], dict(help='Repository to run tests from.', required=True)),
        ]

    @controller.expose(hide=True, help='Schedules a new load test for the given repository.')
    def default(self):
        self.log.info('Inside schedule function.')
