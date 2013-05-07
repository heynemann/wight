#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import tornado.web

logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):

    @staticmethod
    def authenticated(fn):
        def handle(decorated_self, *args, **kw):
            if not 'X-Wight-Auth' in decorated_self.request.headers:
                decorated_self.set_status(401)
                decorated_self.finish()
                return

            fn(decorated_self, *args, **kw)

        handle.__name__ = fn.__name__
        handle.__doc__ = fn.__doc__

        return handle
