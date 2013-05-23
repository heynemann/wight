#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
import requests

import tornado.web

from wight.api.handlers.base import BaseHandler


class ReportHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, uuid):
        test = requests.get("http://0.0.0.0:2367/load-tests/%s/" % uuid)
        self.render('report.html', tests=test.content)


class DiffHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, from_report_hash, to_report_hash):
        self.render('diff.html')


class TrendHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, team_name, project_name, test_full_name):
        self.render('trend.html')
