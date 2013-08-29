#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys
import logging
from tempfile import mkdtemp
from os.path import join

from sh import Command, ErrorReturnCode
from funkload.ReportBuilder import FunkLoadXmlParser
from funkload.MergeResultFiles import MergeResultFiles
import virtualenv

from wight import FUNKLOAD_GIT
from wight.worker.bench_configuration import BenchConfiguration
from wight.worker.config import TestConfig, DEFAULT_CYCLES

fl_run_bench = Command("fl-run-bench")


class FunkLoadTestRunResult(object):
    def __init__(self, exit_code, text, log, result=None, config=None):
        self.exit_code = exit_code
        self.text = text
        self.log = log
        self.result = result
        self.config = config


class FunkLoadTestRunner(object):

    @classmethod
    def run(cls, root_path, test, base_url):
        logging.debug("run test")
        module, class_name, test_name = (test.module, test.class_name, test.test_name)
        temp_path = mkdtemp()

        try:
            logging.debug("creating venv")
            venv_path = "%s/venv" % temp_path.rstrip('/')
            virtualenv.create_environment(
                venv_path,
                site_packages=True,
                unzip_setuptools=True,
                use_distribute=True
            )

            logging.debug("installing funkload")
            pip = Command("%s/bin/pip" % venv_path)
            pip.install(FUNKLOAD_GIT)

            for dep in test.deps:
                logging.debug("install deps")
                pip.install(dep)

            logging.debug("run command: %s" % ("%s/bin/fl-run-test " % venv_path))
            fl_run_test = Command("%s/bin/fl-run-test " % venv_path)
            logging.debug("command run")

            logging.debug("get result")
            result = fl_run_test(module, "%s.%s" % (class_name, test_name), u=base_url, _env={
                "PYTHONPATH": '$PYTHONPATH:%s' % join(root_path.rstrip('/'), "bench")
            }, simple_fetch=True, _cwd=temp_path)

            exit_code = result.exit_code
            text = result.stdout + result.stderr

            with open(join(temp_path, 'funkload.log')) as fl_log:
                logging.debug("write log")
                log = fl_log.read()

        except ErrorReturnCode:
            err = sys.exc_info()[1]
            text = err.stderr
            exit_code = 1
            log = err.stdout + err.stderr
            logging.error(log)


        logging.debug("test run")
        return FunkLoadTestRunResult(exit_code, text, log)


class FunkLoadBenchRunner(object):

    @classmethod
    def run(cls, root_path, test, base_url, workers=[], cycles=DEFAULT_CYCLES, duration=10):
        assert isinstance(test, TestConfig), "The test argument must be of type wight.worker.config.TestConfig"

        #fl-run-bench --distribute --distribute-workers=localhost -u http://www.something.com -c 10:20:30:40:50 -D 30 --simple-fetch geo.py GeoTests.test_geo

        arguments = [test.module, "%s.%s" % (test.class_name, test.test_name)]

        keyword_arguments = dict(
            # keyword arguments
            u=base_url,
            simple_fetch=True,
            c=":".join([str(cycle) for cycle in cycles[test.pressure]]),
            feedback_endpoint=join(root_path, "%s_%s" % (test.class_name, test.test_name)),


            # sh.py options
            _env={
                "PYTHONPATH": '$PYTHONPATH:%s:%s' % (
                    join(root_path.rstrip('/')),
                    join(root_path.rstrip('/'), "bench")
                )
            },
            _cwd=join(root_path, 'bench'),
            _tty_in=True,
            _tty_out=True
        )

        if workers:
            keyword_arguments["distribute"] = True

        cfg = BenchConfiguration(
            test_name=test.test_name,
            title=test.title,
            description=test.description,
            duration=duration,
            log_path=root_path,
            workers=workers
        )
        cfg.calculate_timeout(len(cycles[test.pressure]))
        cfg.save(join(root_path, 'bench', '%s.conf' % test.class_name))

        try:
            result = fl_run_bench(*arguments, **keyword_arguments)
        except ErrorReturnCode:
            err = sys.exc_info()[1]
            return FunkLoadTestRunResult(1, err.stdout + err.stderr, log=err.stderr, result=None, config=None)

        try:
            with open(join(root_path, 'bench', 'funkload.log')) as fl_log:
                log = fl_log.read()

            xml_path = join(root_path, 'bench', 'funkload.xml')
            if workers:
                MergeResultFiles(
                    [join(root_path, 'worker_%s-funkload.xml' % index) for index in range(len(workers))],
                    xml_path
                )

            parser = FunkLoadXmlParser(1.5)
            parser.parse(xml_path)

            return FunkLoadTestRunResult(
                result.exit_code, result.stdout + result.stderr, log=log,
                result=parser.stats, config=parser.config)
        except Exception:
            err = sys.exc_info()[1]
            return FunkLoadTestRunResult(1, "Result STDOUT: %s\nResult STDERR: %s\nResult Parsing Error: %s" % (result.stdout, result.stderr, str(err)), log=None, result=None, config=None)
