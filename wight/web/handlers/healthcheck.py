#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tornado.web

from wight.api.handlers.base import BaseHandler


class HealthCheckHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        self.set_status(200)
        self.write(self.application.config.HEALTHCHECK_TEXT)
        self.finish()
