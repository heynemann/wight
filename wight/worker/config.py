#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import exists

from derpconf.config import Config, generate_config
from yaml import load
try:
    # if libyaml is available we use it, since it's a lot faster
    from yaml import CLoader as Loader
except ImportError:
    # otherwise use pure python implementation
    from yaml import Loader  # NOQA

MINUTES = 60
HOURS = 60 * MINUTES

Config.define('CYCLES', [1, 20, 40, 60, 80, 100], 'The cycles to run in funkload.', 'Funkload')
Config.define('CYCLE_DURATION', 3, 'The cycle duration to run in funkload.', 'Funkload')

Config.define('MONGO_HOST', '127.0.0.1', 'The host where the Mongo server is running.', 'DB')
Config.define('MONGO_PORT', 7777, 'The port that the Mongo server is running.', 'DB')
Config.define('MONGO_DB', 'wight-api', 'The database name we should use for the api in mongo.', 'DB')
Config.define('MONGO_USER', None, 'The user name to authenticate with mongo.', 'DB')
Config.define('MONGO_PASS', None, 'The password to authenticate with mongo.', 'DB')

Config.define('REDIS_HOST', '127.0.0.1', 'The host where the Redis server is running.', 'Cache')
Config.define('REDIS_PORT', 7780, 'The port that Redis server is running.', 'Cache')
Config.define('REDIS_DB_COUNT', 0, 'The number of redis db.', 'Cache')
Config.define('REDIS_PASSWORD', '', 'The redis password', 'Cache')

Config.define('WORKERS', [], 'The workers definition. Each worker should be defined as a dictionary with host, username and password.', 'Workers')

#dsn_url = 'https://726638bb401e4b1580102d1699d07d3e:98c3b4ff108e402abe3ecd2d372e6bb3@app.getsentry.com/4140'
#Config.define('USE_SENTRY', False, 'Should report error to getsentry.com.', 'Sentry')
#Config.define('GETSENTRY_DSN_URL', dsn_url , 'DSN url in getsentry.com.', 'Sentry')


class TestConfig(object):
    def __init__(self, title, description, module, class_name, test_name):
        self.title = title
        self.description = description
        self.module = module
        self.class_name = class_name
        self.test_name = test_name


class WightConfig(object):
    def __init__(self, yaml_text):
        result = load(yaml_text, Loader=Loader)

        self.tests = []

        for test in result.get('tests', []):
            test_obj = TestConfig(
                test.get('title', None),
                test.get('description', None),
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

if __name__ == '__main__':
    generate_config()
