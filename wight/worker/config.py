#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class TestConfig(object):
    def __init__(self, title, module, class_name, test_name):
        self.title = title
        self.module = module
        self.class_name = class_name
        self.test_name = test_name


class WightConfig(object):
    def __init__(self, yaml_text):
        result = load(yaml_text, Loader=Loader)

        self.tests = []
        test_index = 0

        for test in result.get('tests', []):
            default_title = "TEST_%d" % test_index
            test_index += 1

            test_obj = TestConfig(
                test.get('title', default_title),
                test.get('module', None),
                test.get('class', None),
                test.get('test', None)
            )
            self.tests.append(test_obj)
