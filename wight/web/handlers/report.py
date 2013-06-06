#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from datetime import datetime
from json import loads
import requests

import tornado.web

from wight.api.handlers.base import BaseHandler


def format_date(date_as_text):
    date_as_text = date_as_text.replace("T", " ")
    date = datetime.strptime(date_as_text, "%Y-%m-%d %H:%M:%S")
    return date.strftime("%d/%m/%Y %H:%M:%S")


class ReportHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, uuid):
        api_result = requests.get("http://0.0.0.0:2367/load-test-result/%s/" % uuid)
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        kwargs = {
            "test": None,
            "report_date": report_date,
            "uuid": uuid
        }
        if api_result.status_code == 200:
            has_diff = False
            api_content = loads(api_result.content)
            if "result" in api_content:
                test = api_content["result"]
            else:
                test = api_content["results"][0]
            kwargs.update({
                "createdBy": api_content["createdBy"],
                "runAt": api_content["lastModified"],
                "test": test,
                "format_date": format_date,
                "has_diff": has_diff
            })

        self.render('report.html', **kwargs)


class DiffHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, from_report_hash, to_report_hash):
        self.render('diff.html')


class TrendHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, team_name, project_name, test_full_name):
        self.render('trend.html')
