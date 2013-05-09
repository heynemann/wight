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
from wight.cli.auth import AuthController
from wight.cli.target import TargetSetController, TargetGetController
from wight.cli.team import CreateTeamController, ShowTeamController, UpdateTeamController, TeamAddUserController, DeleteTeamController
from wight.cli.user import ShowUserController
from wight.cli.project import CreateProjectController
from wight.models import UserData


class WightApp(foundation.CementApp):
    class Meta:
        label = 'wight'
        base_controller = WightDefaultController

    def __init__(self, label=None, **kw):
        super(WightApp, self).__init__(**kw)
        self.user_data = UserData.load()

    def register_controllers(self):
        self.controllers = [
            AuthController,
            ScheduleController,
            TargetSetController,
            TargetGetController,
            CreateTeamController,
            UpdateTeamController,
            ShowTeamController,
            DeleteTeamController,
            ShowUserController,
            TeamAddUserController,
            CreateProjectController,
        ]

        for controller in self.controllers:
            handler.register(controller)
