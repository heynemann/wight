#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.cli.app import WightApp
from wight.cli.schedule import ScheduleController
from wight.cli.target import TargetSetController, TargetGetController
from tests.base import TestCase


class TestWightApp(TestCase):
    app_class = WightApp

    def setUp(self):
        super(TestWightApp, self).setUp()
        self.reset_backend()
        self.app = WightApp(argv=[], config_files=[])

    def test_wight_app(self):
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_has_proper_controllers(self):
        self.app.setup()

        self.app.register_controllers()

        expect(self.app.controllers).to_length(3)
        expect(self.app.controllers).to_include(ScheduleController)
        expect(self.app.controllers).to_include(TargetSetController)
        expect(self.app.controllers).to_include(TargetGetController)
