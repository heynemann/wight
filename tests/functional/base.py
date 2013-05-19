#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import abspath, join, dirname
from unittest import TestCase as PythonTestCase

from mongoengine import connect

root_path = abspath(join(dirname(__file__), '..', '..'))


class TestCase(PythonTestCase):
    pass


class ModelTestCase(PythonTestCase):
    @classmethod
    def setUpClass(cls):
        connect(
            "mongo-test",
            host="localhost",
            port=7778
        )


class FunkLoadBaseTest(TestCase, ModelTestCase):
    def setUp(self):
        super(FunkLoadBaseTest, self).setUp()
        self.base_url = "http://localhost:2368"
