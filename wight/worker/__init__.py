#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from uuid import UUID
from os.path import join

from wight.models import LoadTest
from wight.worker.repository import Repository
from wight.worker.config import WightConfig
from wight.worker.runners import FunkLoadTestRunner, FunkLoadBenchRunner


class BenchRunner(object):
    def run_project_tests(self, base_path, load_test_uuid, cycles=[10, 20, 30, 40, 50], duration=10):
        load_test = LoadTest.objects(uuid=UUID(load_test_uuid)).first()

        repo = Repository.clone(url=load_test.project.repository, path=base_path)
        bench_path = join(base_path, 'bench')
        cfg = WightConfig.load(join(bench_path, 'wight.yml'))

        is_valid = self.validate_tests(base_path, repo, cfg, load_test)

        if is_valid:
            for test in cfg.tests:
                fl_result = FunkLoadBenchRunner.run(
                    base_path, test, load_test.base_url, cycles=cycles, duration=duration
                )

                result = LoadTest.get_data_from_funkload_results(fl_result.config, fl_result.result)
                load_test.add_result(result, xml=fl_result.xml, log=fl_result.text)

            load_test.status = "Finished"
            load_test.save()

    def validate_tests(self, base_path, repo, config, load_test):
        for test in config.tests:
            result = FunkLoadTestRunner.run(
                base_path, test.module, test.class_name,
                test.test_name, load_test.base_url
            )
            if result.exit_code != 0:
                return False

        return True
