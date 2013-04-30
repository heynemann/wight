#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import abspath, join, dirname
import logging

import redis
import tornado.web
import tornado.wsgi
from tornado.web import url
#from raven import Client

#from wight.api.utils.redis_session import RedisSessionStore
#from wight.api.cache import RedisCache
from wight.api.handlers.healthcheck import HealthCheckHandler

#class FakeSentry(object):
    #def __init__(self, dsn):
        #self.dsn = dsn

    #def captureException(self, exc_info, extra):
        #import traceback
        #logging.error(''.join(traceback.format_exception(exc_info[0], exc_info[1], exc_info[2])))


def configure_app(self, config=None, log_level='INFO', debug=False, static_path=None):
    static_path = abspath(join(dirname(__file__), 'static'))

    self.config = config

    handlers = [
        url(r'/healthcheck(?:/|\.html)?', HealthCheckHandler, name="healthcheck"),
    ]

    logging.info("Connecting to redis on {0}:{1}/{2}".format(self.config.REDIS_HOST, self.config.REDIS_PORT, self.config.REDIS_DB_COUNT))
    self.redis = redis.StrictRedis(
        host=self.config.REDIS_HOST,
        port=self.config.REDIS_PORT,
        db=self.config.REDIS_DB_COUNT,
        password=self.config.REDIS_PASSWORD
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
        "static_url_prefix": self.config.STATIC_URL
    }

    if debug:
        options['debug'] = True
        config.NUMBER_OF_FORKS = 1

    return handlers, options


class WightApp(tornado.web.Application):

    def __init__(self, config=None, log_level='INFO', debug=False, static_path=None):
        handlers, options = configure_app(self, config, log_level, debug, static_path)
        super(WightApp, self).__init__(handlers, **options)
