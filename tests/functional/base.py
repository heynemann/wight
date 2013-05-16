#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

#import sys
from os.path import abspath, join, dirname

from unittest import TestCase as PythonTestCase

root_path = abspath(join(dirname(__file__), '..', '..'))


class TestCase(PythonTestCase):
    pass


class FunkLoadBaseTest(TestCase):
    def setUp(self):
        self.base_url = "http://localhost:2368"
        #sys.path.append(join(root_path, 'bench'))

    #def tearDown(self):
        #sys.path.pop()
