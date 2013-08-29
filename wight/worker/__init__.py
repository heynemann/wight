#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from os import mkdir

import sys
from uuid import UUID
from os.path import join, expanduser, abspath
import argparse
import logging
from tempfile import mkdtemp
from datetime import datetime

from pygit2 import GIT_SORT_TIME
from pyres.worker import Worker
from pyres import ResQ
from mongoengine import connect

from wight.models import LoadTest, Commit
from wight.worker.repository import Repository
from wight.worker.config import WightConfig, Config, DEFAULT_CYCLES
from wight.worker.runners import FunkLoadTestRunner, FunkLoadBenchRunner


LOGS = {
    0: 'error',
    1: 'warning',
    2: 'info',
    3: 'debug'
}


class TestNotValidError(Exception):
    pass


class WorkerJob(object):
    queue = 'wight'
    config = None

    @staticmethod
    def perform(load_test_uuid):
        temp_path = mkdtemp()
        runner = BenchRunner()

        runner.run_project_tests(
            base_path=temp_path, load_test_uuid=load_test_uuid,
            workers=WorkerJob.resq.config.WORKERS,
            cycles=WorkerJob.resq.config.CYCLES, duration=WorkerJob.resq.config.CYCLE_DURATION
        )


class BenchRunner(object):

    yml_file_content = """
tests:
  -
    title: Test in %s
    description: Simple test schedule to hit %s.
    module: test_simple
    class: SimpleTestTest
    test: test_simple
    pressure: small
"""
    test_file_content = """
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase


class SimpleTestTest(FunkLoadTestCase):
    def setUp(self):
        self.server_url = '%s/' % (self.conf_get('main', 'url').rstrip('/'),)

    def test_simple(self):
        self.get(self.server_url, description='Get url')

if __name__ == '__main__':
    unittest.main()

"""

    def _save_last_commit(self, load_test, repo):
        last_commit = tuple(repo.walk(repo.head.target, GIT_SORT_TIME))[0]
        load_test.last_commit = Commit.from_pygit(last_commit)
        load_test.save()

    def _clone_repository(self, base_path, load_test):
        repo = Repository.clone(url=load_test.project.repository, path=base_path, branch=load_test.git_branch)
        self._save_last_commit(load_test, repo)
        return repo

    def run_project_tests(self, base_path, load_test_uuid, workers=[], cycles=DEFAULT_CYCLES, duration=10):
        logging.debug("loading test")
        load_test = LoadTest.objects(uuid=UUID(load_test_uuid)).first()
        load_test.status = "Running"
        load_test.running_since = datetime.utcnow()
        load_test.save()
        logging.debug("test saved")

        try:
            cfg = self._build_test_config(base_path, load_test)
            self._run_config_tests(cfg, base_path, load_test, workers, cycles, duration)
            load_test.status = "Finished"
            load_test.save()
        except Exception:
            err = sys.exc_info()[1]
            logging.error(err)
            load_test.status = "Failed"
            load_test.error = str(err)
            load_test.save()

    def validate_tests(self, base_path, config, load_test):
        logging.debug("test validation")
        if not config:
            logging.debug("not config")
            raise TestNotValidError("The wight.yml file was not found in project repository bench folder.")

        for test in config.tests:
            result = FunkLoadTestRunner.run(base_path, test, load_test.base_url)
            if result.exit_code != 0:
                logging.debug("test not valid: %s" % test.test_name)
                logging.error(result.log)
                raise TestNotValidError("The test '%s.%s.%s' running in '%s' is not valid (%s)" %
                                        (test.module, test.class_name,
                                        test.test_name, load_test.base_url, result.text))
        logging.debug("finish test validation")

    def _create_simple_test(self, base_path, load_test):
        mkdir(join(base_path, "bench"))
        init_file = open(join(base_path, "bench/__init__.py"), "w")
        init_file.close()
        wight_file = open(join(base_path, "bench/wight.yml"), "w")
        wight_file.write(self.yml_file_content % (load_test.base_url, load_test.base_url))
        wight_file.close()
        test_file = open(join(base_path, "bench/test_simple.py"), "w")
        test_file.write(self.test_file_content)
        test_file.close()

    def _build_test_config(self, base_path, load_test):
        logging.debug("build config")
        if load_test.simple:
            self._create_simple_test(base_path, load_test)
        else:
            self._clone_repository(base_path, load_test)
        cfg = self._load_config_from_yml(base_path)
        self.validate_tests(base_path, cfg, load_test)
        return cfg

    def _load_config_from_yml(self, base_path):
        logging.debug("parse yml")
        bench_path = join(base_path, 'bench')
        return WightConfig.load(join(bench_path, 'wight.yml'))

    def _run_config_tests(self, cfg, base_path, load_test, workers, cycles, duration):
        logging.debug("running tests")
        for test in cfg.tests:
            kw = dict(
                root_path=base_path,
                test=test,
                base_url=load_test.base_url,
                cycles=cycles,
                duration=duration
            )

            if workers:
                kw['workers'] = workers

            fl_result = FunkLoadBenchRunner.run(**kw)

            if fl_result.exit_code != 0:
                load_test.status = "Failed"
                load_test.error = fl_result.text
                load_test.save()
                return

            logging.debug("create result for %s" % test.test_name)
            result = LoadTest.get_data_from_funkload_results(fl_result.config, fl_result.result)

            load_test.add_result(result, log=fl_result.text)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', '-c', help="Path to configuration file.")
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Log level: v=warning, vv=info, vvv=debug.')
    options = parser.parse_args(args)

    log_level = LOGS[options.verbose].upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if options.conf:
        cfg = Config.load(abspath(expanduser(options.conf)))
    else:
        cfg = Config()

    conn = ResQ(server="%s:%s" % (cfg.REDIS_HOST, cfg.REDIS_PORT), password=cfg.REDIS_PASSWORD)
    conn.config = cfg

    connect(
        cfg.MONGO_DB,
        host=cfg.MONGO_HOST,
        port=cfg.MONGO_PORT,
        username=cfg.MONGO_USER,
        password=cfg.MONGO_PASS
    )

    print
    print("--- Wight worker started ---")
    print
    Worker.run([WorkerJob.queue], conn)
    print
    print "--- Wight worker killed ---"
    print

if __name__ == '__main__':
    main()
