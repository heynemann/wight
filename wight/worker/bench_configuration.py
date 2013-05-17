#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com


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
            sleep_time_max=0.5):

        self.test_name = test_name
        self.title = title
        self.description = description
        self.duration = duration
        self.startup_delay = startup_delay
        self.cycle_time = cycle_time
        self.sleep_time = sleep_time
        self.sleep_time_min = sleep_time_min
        self.sleep_time_max = sleep_time_max

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
            conf_file.write(
                """[main]
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
            )
