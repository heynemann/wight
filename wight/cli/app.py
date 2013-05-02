#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import foundation, handler
import slumber

from wight.cli.base import WightDefaultController
from wight.cli.schedule import ScheduleController
from wight.cli.target import TargetSetController, TargetGetController


class WightApp(foundation.CementApp):
    class Meta:
        label = 'wight'
        base_controller = WightDefaultController

    def __init__(self, label=None, **kw):
        super(WightApp, self).__init__(**kw)
        self.api = slumber.API("http://localhost:8000/v1/")

    def register_controllers(self):
        self.controllers = [
            ScheduleController,
            TargetSetController,
            TargetGetController
        ]

        for controller in self.controllers:
            handler.register(controller)
