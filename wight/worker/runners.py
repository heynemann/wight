#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from tempfile import mkdtemp
from os.path import join

from sh import Command

fl_run_test = Command("fl-run-test")


class FunkLoadTestRunResult(object):
    def __init__(self, exit_code, text, log, xml):
        self.exit_code = exit_code
        self.text = text
        self.log = log
        self.xml = xml


class FunkLoadTestRunner(object):

    @classmethod
    def run(cls, root_path, module, class_name, test_name, base_url):
        temp_path = mkdtemp()
        result = fl_run_test(module, "%s.%s" % (class_name, test_name), u=base_url, _env={
            "PYTHONPATH": '$PYTHONPATH:%s' % join(root_path.rstrip('/'), "bench")
        }, simple_fetch=True, _cwd=temp_path)

        with open(join(temp_path, 'funkload.log')) as fl_log:
            log = fl_log.read()

        with open(join(temp_path, 'funkload.xml')) as fl_xml:
            xml = fl_xml.read()

        return FunkLoadTestRunResult(result.exit_code, result.stdout + result.stderr, log, xml)
