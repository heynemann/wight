#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import controller

from wight.cli.base import WightBaseController
from wight.models import UserData


class TargetSetController(WightBaseController):
    class Meta:
        label = 'target-set'
        stack_on = 'base'
        description = 'Sets target for wight to use.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['target'], dict(help='Target to connect to.')),
        ]

    @controller.expose(hide=False, aliases=["target-set"], help='Sets wight target to the specified target.')
    def default(self):
        self.load_conf()

        target = self.arguments.target
        self.line_break()
        self.putsuccess("Wight target set to '%s%s%s'. In order to login with wight, use '%swight login%s'." % (
            self.keyword_color, target, self.reset_success,
            self.commands_color, self.reset_success
        ))
        self.line_break()

        ud = UserData.load()
        if ud is None:
            ud = UserData(target=target)
        else:
            ud.target = target

        ud.save()


class TargetGetController(WightBaseController):
    class Meta:
        label = 'target-get'
        stack_on = 'base'
        description = 'Gets the target wight is using currently.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
        ]

    @controller.expose(hide=False, aliases=["target-get"], help='Gets the target wight is using currently.')
    def default(self):
        self.load_conf()

        user_data = UserData.load()

        if user_data is None:
            self.write("No target set.")
            return

        self.write("Current target set to '%s'." % user_data.target)
