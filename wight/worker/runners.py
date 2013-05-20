#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys
from tempfile import mkdtemp
from os.path import join

from sh import Command, ErrorReturnCode
from funkload.ReportBuilder import FunkLoadXmlParser

from wight.worker.bench_configuration import BenchConfiguration
from wight.worker.config import TestConfig

fl_run_test = Command("fl-run-test")
fl_run_bench = Command("fl-run-bench")


class FunkLoadTestRunResult(object):
    def __init__(self, exit_code, text, log, xml, result=None, config=None):
        self.exit_code = exit_code
        self.text = text
        self.log = log
        self.xml = xml
        self.result = result
        self.config = config


class FunkLoadTestRunner(object):

    @classmethod
    def run(cls, root_path, module, class_name, test_name, base_url):
        temp_path = mkdtemp()

        try:
            result = fl_run_test(module, "%s.%s" % (class_name, test_name), u=base_url, _env={
                "PYTHONPATH": '$PYTHONPATH:%s' % join(root_path.rstrip('/'), "bench")
            }, simple_fetch=True, _cwd=temp_path)

            exit_code = result.exit_code
            text = result.stdout + result.stderr

            with open(join(temp_path, 'funkload.log')) as fl_log:
                log = fl_log.read()

            with open(join(temp_path, 'funkload.xml')) as fl_xml:
                xml = fl_xml.read()

        except ErrorReturnCode:
            err = sys.exc_info()[1]
            text = err.stderr
            exit_code = 1
            log = err.stdout + err.stderr
            xml = None

        return FunkLoadTestRunResult(exit_code, text, log, xml)


class FunkLoadBenchRunner(object):
    @classmethod
    def run(cls, root_path, test, base_url, workers=[], cycles=[10, 20, 30, 40, 50], duration=10):
        assert isinstance(test, TestConfig), "The test argument must be of type wight.worker.config.TestConfig"
        temp_path = mkdtemp()

        #fl-run-bench --distribute --distribute-workers=localhost -u http://api.qa01.globoi.com -c 10:20:30:40:50 -D 30 --simple-fetch geo.py GeoTests.test_geo

        arguments = [test.module, "%s.%s" % (test.class_name, test.test_name)]

        keyword_arguments = dict(
            # keyword arguments
            u=base_url, simple_fetch=True,
            c=":".join([str(cycle) for cycle in cycles]),

            # sh.py options
            _env={
                "PYTHONPATH": '$PYTHONPATH:%s' % join(root_path.rstrip('/'), "bench")
            },
            _cwd=temp_path
        )

        cfg = BenchConfiguration(
            test_name=test.test_name,
            title=test.title,
            description=test.description,
            duration=duration
        )

        cfg.save(join(temp_path, '%s.conf' % test.class_name))

        result = fl_run_bench(*arguments, **keyword_arguments)

        with open(join(temp_path, 'funkload.log')) as fl_log:
            log = fl_log.read()

        xml_path = join(temp_path, 'funkload.xml')
        with open(xml_path) as fl_xml:
            xml = fl_xml.read()

        parser = FunkLoadXmlParser(1.5)
        parser.parse(xml_path)

        return FunkLoadTestRunResult(
            result.exit_code, result.stdout + result.stderr, log=log,
            xml=xml, result=parser.stats, config=parser.config)
