#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import abspath, join, dirname
import logging

import redis
from mongoengine import connect
import tornado.web
import tornado.wsgi
from tornado.web import url
#from raven import Client

from wight.web.handlers.healthcheck import HealthCheckHandler
from wight.web.handlers.report import ReportHandler, DiffHandler, TrendHandler

#class FakeSentry(object):
    #def __init__(self, dsn):
        #self.dsn = dsn

    #def captureException(self, exc_info, extra):
        #import traceback
        #logging.error(''.join(traceback.format_exception(exc_info[0], exc_info[1], exc_info[2])))


def configure_app(self, config=None, log_level='INFO', debug=False, static_path=None):
    if static_path is None:
        static_path = abspath(join(dirname(__file__), 'static'))
    template_path = abspath(join(dirname(__file__), 'templates'))

    self.config = config

    handlers = [
        url(r'/healthcheck(?:/|\.html)?', HealthCheckHandler, name="healthcheck"),
        url(r'/report/(?P<report_hash>.+?)(?:/|\.html)?', ReportHandler, name="report"),
        url(r'/diff/(?P<from_report_hash>.+?)/(?P<to_report_hash>.+?)/?', DiffHandler, name="diff"),
        url(r'/trend/(?P<team_name>.+?)/(?P<project_name>.+?)/(?P<test_full_name>.+?)/?', TrendHandler, name="trend"),
    ]

    logging.info("Connecting to redis on {0}:{1}/{2}".format(self.config.REDIS_HOST, self.config.REDIS_PORT, self.config.REDIS_DB_COUNT))
    self.redis = redis.StrictRedis(
        host=self.config.REDIS_HOST,
        port=self.config.REDIS_PORT,
        db=self.config.REDIS_DB_COUNT,
        password=self.config.REDIS_PASSWORD
    )

    connect(
        self.config.MONGO_DB,
        host=self.config.MONGO_HOST,
        port=self.config.MONGO_PORT,
        username=self.config.MONGO_USER,
        password=self.config.MONGO_PASS
    )

    #self.session_store = RedisSessionStore(
        #self.redis,
        #expire=self.config.REDIS_SESSION_EXPIRATION
    #)

    #self.cache = RedisCache(self.redis)

    #if self.config.USE_SENTRY:
        #self.sentry = Client(self.config.GETSENTRY_DSN_URL)
    #else:
        #self.sentry = FakeSentry(self.config.GETSENTRY_DSN_URL)

    options = {
        "cookie_secret": self.config.COOKIE_SECRET,
        "static_path": static_path,
        "static_url_prefix": self.config.STATIC_URL,
        "template_path": template_path
    }

    if debug:
        options['debug'] = True
        config.NUMBER_OF_FORKS = 1

    return handlers, options


class WightWebApp(tornado.web.Application):

    def __init__(self, config=None, log_level='INFO', debug=False, static_path=None):
        handlers, options = configure_app(self, config, log_level, debug, static_path)
        super(WightWebApp, self).__init__(handlers, **options)
