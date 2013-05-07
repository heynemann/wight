#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import expanduser

from cement.core import foundation, handler

from wight.cli.base import WightDefaultController
from wight.cli.schedule import ScheduleController
from wight.cli.auth import AuthController
from wight.cli.target import TargetSetController, TargetGetController
from wight.cli.team import CreateTeamController, ShowTeamController
from wight.models import UserData


class WightApp(foundation.CementApp):
    class Meta:
        label = 'wight'
        base_controller = WightDefaultController

    def __init__(self, label=None, **kw):
        super(WightApp, self).__init__(**kw)
        self.user_data = UserData.load(expanduser("~/.wight"))

    def register_controllers(self):
        self.controllers = [
            AuthController,
            ScheduleController,
            TargetSetController,
            TargetGetController,
            CreateTeamController,
            ShowTeamController,
        ]

        for controller in self.controllers:
            handler.register(controller)
