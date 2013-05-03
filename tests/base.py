#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import dirname, abspath, join
from unittest import TestCase as PythonTestCase

from mock import Mock
from tornado.testing import AsyncHTTPTestCase
from cement.utils import test
from mongoengine import connect

from wight.api.app import WightApp
from wight.api.config import Config
from wight.models import User

ROOT_PATH = abspath(join(dirname(__file__), '..'))


class TestCase(test.CementTestCase):
    def make_controller(self, cls, app=None, *args, **kw):
        if app is None:
            app = self.make_app(argv=args)
            app.setup()

        pargs = Mock(**kw)
        controller = cls(pargs=pargs)
        controller.app = app
        controller.log = Mock()

        return controller

    def fixture_for(self, filename):
        return join(ROOT_PATH, 'tests', 'fixtures', filename)


class ApiTestCase(AsyncHTTPTestCase):
    def make_app(self, config=None):
        if not config:
            config = Config()
        return WightApp(config=config)


class ModelTestCase(PythonTestCase):
    @classmethod
    def setUpClass(cls):
        connect(
            "mongo-test",
            host="localhost",
            port=7777
        )

        User.objects.delete()
