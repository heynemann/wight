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
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        kwargs = {
            "uuid": uuid,
            "test": None,
            "format_date": format_date,
            "report_date": report_date,
        }
        api_result = requests.get("http://0.0.0.0:2367/load-test-result/%s/" % uuid)
        if api_result.status_code == 200:
            api_content = loads(api_result.content)
            if "result" in api_content:
                test = api_content["result"]
            else:
                test = api_content["results"][0]

            last_result = self._get_last_result(uuid)
            kwargs.update({
                "createdBy": api_content["createdBy"],
                "runAt": api_content["lastModified"],
                "test": test,
                "last_result": last_result
            })

        self.render('report.html', **kwargs)

    def _get_last_result(self, uuid):
        api_result = requests.get("http://0.0.0.0:2367/load-test-result/%s/last/" % uuid)
        if api_result.status_code == 200:
            api_content = loads(api_result.content)
            return api_content["uuid"]
        return None


class DiffHandler(BaseHandler):

    def add_test_result_to_kwargs(self, kwargs, uuid, test_name):
        api_result = requests.get("http://0.0.0.0:2367/load-test-result/%s/" % uuid)
        if api_result.status_code == 200:
            api_content = loads(api_result.content)
            test = api_content["result"]
            kwargs.update({
                "project_name": api_content["projectName"],
                "%s_created_by" % test_name: api_content["createdBy"],
                "%s_run_at" % test_name: api_content["lastModified"],
                "%s_test" % test_name: test,
            })

    @tornado.web.asynchronous
    def get(self, reference_uuid, challenger_uuid):
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        kwargs = {
            "reference_uuid": reference_uuid,
            "challenger_uuid": challenger_uuid,
            "reference_test": None,
            "challenger_test": None,
            "format_date": format_date,
            "report_date": report_date,
        }
        self.add_test_result_to_kwargs(kwargs, reference_uuid, "reference")
        self.add_test_result_to_kwargs(kwargs, challenger_uuid, "challenger")
        self.render('diff.html', **kwargs)


class TrendHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, team, project, module, class_name, test):
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        kwargs = {
            "team": team,
            "project": project,
            "module": module,
            "class_name": class_name,
            "test": test,
            "full_name": "%s.%s.%s" % (module, class_name, test),
            "results": [],
            "format_date": format_date,
            "report_date": report_date,
        }
        api_result = requests.get("http://0.0.0.0:2367/results/%s/%s/%s/%s/%s/" % (team, project, module, class_name, test))
        if api_result.status_code == 200:
            results = loads(api_result.content)
            concurrent_users = []
            for result in results:
                for cycle in result["cycles"]:
                    if not cycle["concurrentUsers"] in concurrent_users:
                        concurrent_users.append(cycle["concurrentUsers"])
            concurrent_users.sort()

            kwargs.update({
                "results": results,
                "concurrent_users": concurrent_users
            })
        self.render('trend.html', **kwargs)
