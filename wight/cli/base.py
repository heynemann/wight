#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys

from cement.core import controller

from wight.models import UserData


class WightBaseController(controller.CementBaseController):
    def __init__(self, *args, **kw):
        self.arguments = None
        if 'pargs' in kw:
            pargs = kw['pargs']
            del kw['pargs']
            self.arguments = pargs

        super(WightBaseController, self).__init__(*args, **kw)

    def _parse_args(self):
        super(WightBaseController, self)._parse_args()

        if self.arguments is None:
            self.arguments = self.app.pargs

    def load_conf(self):
        conf_path = self.arguments and self.arguments.conf or None
        if conf_path is None:
            conf_path = UserData.DEFAULT_PATH

        #TODO: load config using derpconf

        self.log.info('Using configuration file in %s.' % conf_path)

    def write(self, msg):
        sys.stdout.write('%s\n' % msg)


class WightDefaultController(WightBaseController):
    class Meta:
        label = 'base'
        description = 'wight load testing scheduler and tracker.'

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
