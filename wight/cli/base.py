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
from six.moves import input

from wight.cli.config import Config
from wight.errors import TargetNotSetError, UnauthenticatedError


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

        self.log.info('Using configuration file in %s.' % conf_path)
        if conf_path and exists(conf_path):
            self.config = Config.load(conf_path)
        else:
            self.config = Config()

    def write(self, msg):
        sys.stdout.write('%s\n' % msg)

    def get_pass(self, msg):
        return getpass.getpass(prompt="%s " % msg)

    def ask_for(self, msg):
        return input("%s " % msg)

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
        response = requests.post(url, data=data, headers=headers)

        def __enter__(self):
            return response

        def __exit__(self, exc_type, exc_val, exc_tb):
            import ipdb; ipdb.set_trace()

        return response

    @staticmethod
    def authenticated(fn):
        def handle(decorated_self, *args, **kw):
            user = None
            if hasattr(decorated_self, 'app') and hasattr(decorated_self.app, 'user_data'):
                user = decorated_self.app.user_data

            if user is None or not user.target:
                raise TargetNotSetError()

            if not user.token:
                raise UnauthenticatedError()

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


class ConnectedController():
    def __init__(self, controller):
        self.controller = controller

    def __enter__(self):
        if self.controller.app.user_data is None:
            raise RuntimeError("Need to set target before trying to access api")
        url = join(self.controller.app.user_data.target.rstrip('/'), 'healthcheck')
        requests.get(url)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_type == requests.ConnectionError:
            ex = exc_val
            self.controller.log.error(ex)
            target = self.controller.app.user_data.target
            self.controller.write("The server did not respond. Check your connection with the target '%s'." % target)
            return True
