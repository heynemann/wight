#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import foundation, handler

from wight.cli.base import WightDefaultController
from wight.cli.schedule import ScheduleController
from wight.cli.target import TargetSetController, TargetGetController


class WightApp(foundation.CementApp):
    class Meta:
        label = 'wight'
        base_controller = WightDefaultController

    def register_controllers(self):
        self.controllers = [
            ScheduleController,
            TargetSetController,
            TargetGetController
        ]

        for controller in self.controllers:
            handler.register(controller)
