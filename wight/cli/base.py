#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys
from os.path import exists, join
import getpass

from cement.core import controller
import requests

from wight.models import UserData
from wight.cli.config import Config
from wight.errors import TargetNotSetError


class WightBaseController(controller.CementBaseController):
    def __init__(self, *args, **kw):
        self.arguments = None
        if 'pargs' in kw:
            pargs = kw['pargs']
            del kw['pargs']
            self.arguments = pargs

        super(WightBaseController, self).__init__(*args, **kw)
        self.ignored += ['api']

    def _parse_args(self):
        super(WightBaseController, self)._parse_args()

        if self.arguments is None:
            self.arguments = self.app.pargs

    def load_conf(self):
        conf_path = self.arguments and self.arguments.conf or None
        if conf_path is None:
            conf_path = UserData.DEFAULT_PATH

        self.log.info('Using configuration file in %s.' % conf_path)
        if exists(conf_path):
            self.config = Config.load(conf_path)
        else:
            self.config = Config()

    def write(self, msg):
        sys.stdout.write('%s\n' % msg)

    def get_pass(self, msg):
        return getpass.getpass(prompt="%s " % msg)

    def ask_for(self, msg):
        return raw_input("%s " % msg)

    def api(self, path, headers={}):
        if self.app.user_data is None:
            raise RuntimeError("Need to set target before trying to access api")
        if self.app.user_data.token:
            headers.update({"X-Wight-Auth": self.app.user_data.token})
        url = join(self.app.user_data.target.rstrip('/'), path.lstrip('/'))
        return requests.get(url, headers=headers)

    def post(self, path, data={}, headers={}):
        if self.app.user_data is None:
            raise RuntimeError("Need to set target before trying to access api")
        headers.update({"X-Wight-Auth": self.app.user_data.token})
        target = self.app.user_data.target.rstrip('/')
        data.update({"target": target})
        url = join(target, path.lstrip('/'))
        return requests.post(url, data=data, headers=headers)

    @staticmethod
    def authenticated(fn):
        def handle(decorated_self, *args, **kw):
            user = UserData.load()
            if user is None or not user.target:
                raise TargetNotSetError()
            fn(decorated_self, *args, **kw)

        handle.__name__ = fn.__name__
        handle.__doc__ = fn.__doc__

        return handle


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
