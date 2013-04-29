#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import controller


class WightBaseController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = "wight load testing scheduler and tracker."

        #config_defaults = dict(
            #foo='bar',
            #some_other_option='my default value',
        #)

        #arguments = [
            #(['-f', '--foo'], dict(action='store', help='the notorious foo option')),
            #(['-C'], dict(action='store_true', help='the big C option'))
        #]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()
