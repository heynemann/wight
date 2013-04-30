#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import tornado.web

logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    pass
