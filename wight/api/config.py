#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import multiprocessing

from derpconf.config import Config, generate_config

MINUTES = 60
HOURS = 60 * MINUTES

Config.define('COOKIE_SECRET', '1617401289404f2182bqwelf7cddd0f', 'To sign secure cookie info.', 'Basic')

Config.define('MONGO_HOST', '127.0.0.1', 'The host where the Mongo server is running.', 'DB')
Config.define('MONGO_PORT', 7777, 'The port that the Mongo server is running.', 'DB')
Config.define('MONGO_DB', 'wight-api', 'The database name we should use for the api in mongo.', 'DB')
Config.define('MONGO_USER', None, 'The user name to authenticate with mongo.', 'DB')
Config.define('MONGO_PASS', None, 'The password to authenticate with mongo.', 'DB')

Config.define('REDIS_HOST', '127.0.0.1', 'The host where the Redis server is running.', 'Cache')
Config.define('REDIS_PORT', 7780, 'The port that Redis server is running.', 'Cache')
Config.define('REDIS_DB_COUNT', 0, 'The number of redis db.', 'Cache')
Config.define('REDIS_PASSWORD', '', 'The redis password', 'Cache')
Config.define('REDIS_SESSION_EXPIRATION', 7200, 'Time for session expiration in Redis.', 'Cache')

Config.define('NUMBER_OF_FORKS', multiprocessing.cpu_count(), 'Number of forks to use for tornado process. Defaults to number of cpus.', 'Runtime')
Config.define('HEALTHCHECK_TEXT', 'WORKING', 'Default text for the healthcheck route.', 'Runtime')

Config.define('STATIC_URL', '/static/', 'Static files route.', 'Static')

#dsn_url = 'https://726638bb401e4b1580102d1699d07d3e:98c3b4ff108e402abe3ecd2d372e6bb3@app.getsentry.com/4140'
#Config.define('USE_SENTRY', False, 'Should report error to getsentry.com.', 'Sentry')
#Config.define('GETSENTRY_DSN_URL', dsn_url , 'DSN url in getsentry.com.', 'Sentry')

if __name__ == '__main__':
    generate_config()
