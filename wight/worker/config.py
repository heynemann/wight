#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import exists

from yaml import load
try:
    # if libyaml is available we use it, since it's a lot faster
    from yaml import CLoader as Loader
except ImportError:
    # otherwise use pure python implementation
    from yaml import Loader  # NOQA


class TestConfig(object):
    def __init__(self, module, class_name, test_name):
        self.module = module
        self.class_name = class_name
        self.test_name = test_name


class WightConfig(object):
    def __init__(self, yaml_text):
        result = load(yaml_text, Loader=Loader)

        self.tests = []

        for test in result.get('tests', []):
            test_obj = TestConfig(
                test.get('module', None),
                test.get('class', None),
                test.get('test', None)
            )
            self.tests.append(test_obj)

    @classmethod
    def load(cls, path):
        if not exists(path):
            return None

        with open(path, 'r') as yaml_file:
            return cls(yaml_file.read())
