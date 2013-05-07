#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
import six
from json import loads
from cement.core import controller

from wight.cli.base import WightBaseController, ConnectedController


class ShowUserController(WightBaseController):
    class Meta:
        label = 'user-info'
        stack_on = 'base'
        description = 'Shows user info'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
        ]

    @controller.expose(hide=False, aliases=["user-info"], help='Show user info.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        with ConnectedController(self):
            response = self.api("/user/info")
            if response.status_code == 200:
                content = response.content
                if isinstance(content, six.binary_type):
                    content = content.decode('utf-8')
                content = loads(content)
                self.write("User: %s" % content['user']['email'])
            elif response.status_code == 401:
                self.write("User not logged in. Run wight authenticate")
