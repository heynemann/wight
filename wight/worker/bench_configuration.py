#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys


class BenchConfiguration(object):
    def __init__(
            self,
            test_name,
            title,
            description,
            duration=10,
            startup_delay=0.01,
            cycle_time=1,
            sleep_time=0.01,
            sleep_time_min=0.0,
            sleep_time_max=0.5,
            log_path="",
            workers=[]):

        self.test_name = test_name
        self.title = title
        self.description = description
        self.duration = duration
        self.startup_delay = startup_delay
        self.cycle_time = cycle_time
        self.sleep_time = sleep_time
        self.sleep_time_min = sleep_time_min
        self.sleep_time_max = sleep_time_max
        self.log_path = log_path
        self.workers = workers

    def to_dict(self):
        return {
            'test_name': self.test_name,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'startup_delay': self.startup_delay,
            'cycle_time': self.cycle_time,
            'sleep_time': self.sleep_time,
            'sleep_time_min': self.sleep_time_min,
            'sleep_time_max': self.sleep_time_max
        }

    def save(self, conf_path):
        with open(conf_path, 'w') as conf_file:
            main_section = """[main]
title=%(title)s
description=%(description)s

[bench]
duration=%(duration)d
startup_delay = %(startup_delay).2f
cycle_time = %(cycle_time)d
sleep_time = %(sleep_time).2f
sleep_time_min = %(sleep_time_min).2f
sleep_time_max = %(sleep_time_max).2f

[%(test_name)s]
description=%(description)s
""" % self.to_dict()

            conf_file.write(main_section)

            if self.workers:
                conf_file.write("""
[distribute]
log_path = %s
python_bin = %s
funkload_location=https://github.com/nuxeo/FunkLoad/archive/master.zip
                """.strip() % (self.log_path, sys.executable))

                conf_file.write("\n")
                worker_names = " ".join(["worker_%d" % i for i in range(len(self.workers))])
                workers = ["""
[workers]
hosts = %s
                """.strip() % worker_names]

                conf_file.write("\n")
                for index, worker in enumerate(self.workers):
                    workers.append("""
[worker_%s]
host = %s
username = %s
                    """.strip() % (index, worker['host'], worker['user']))
                    if 'password' in worker:
                        workers.append('password = %s' % worker['password'])
                    if 'ssh_key' in worker:
                        workers.append('ssh_key = %s' % worker['ssh_key'])

                conf_file.write("\n".join(workers))
