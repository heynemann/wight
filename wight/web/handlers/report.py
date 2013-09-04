#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from datetime import datetime
from json import loads

import tornado.web

from wight.web.handlers.base import BaseHandler, format_date


class ReportHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, uuid):
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        kwargs = {
            "version": self.version(),
            "uuid": uuid,
            "test": None,
            "format_date": format_date,
            "report_date": report_date,
        }
        api_result = self.get_api("load-test-result/%s/" % uuid)
        if api_result.status_code == 200:
            api_content = loads(api_result.content)
            if "result" in api_content:
                test = api_content["result"]
            else:
                test = api_content["results"][0]

            last_result = self._get_last_result(uuid)
            kwargs.update({
                "team": api_content["team"],
                "project": api_content["project"],
                "createdBy": api_content["createdBy"],
                "runAt": api_content["lastModified"],
                "test": test,
                "last_result": last_result
            })

        self.render('report.html', **kwargs)
        self.finish()

    def _get_last_result(self, uuid):
        api_result = self.get_api("load-test-result/%s/last/" % uuid)
        if api_result.status_code == 200:
            api_content = loads(api_result.content)
            return api_content["uuid"]
        return None


class DiffHandler(BaseHandler):

    def add_test_result_to_kwargs(self, kwargs, uuid, test_name):
        api_result = self.get_api("load-test-result/%s/" % uuid)
        if api_result.status_code == 200:
            api_content = loads(api_result.content)
            test = api_content["result"]
            kwargs.update({
                "team": api_content["team"],
                "project": api_content["project"],
                "%s_created_by" % test_name: api_content["createdBy"],
                "%s_run_at" % test_name: api_content["lastModified"],
                "%s_test" % test_name: test,
            })

    @tornado.web.asynchronous
    def get(self, reference_uuid, challenger_uuid):
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        kwargs = {
            "version": self.version(),
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

    def _get_concurrent_users_for_results(self, results):
        return [[cycle["concurrentUsers"] for cycle in result["cycles"]] for result in results]

    def _get_concurrent_users_for_response_time(self, results):
        concurrent_users = self._get_concurrent_users_for_results(results)
        return sorted(set(concurrent_users[0]).intersection(*concurrent_users))

    def _get_concurrent_users_for_apdex(self, results):
        concurrent_users = self._get_concurrent_users_for_results(results)
        return sorted(set(concurrent_users[0]).intersection(*concurrent_users))

    def _get_page_values_for(self, page_data_type, results):
        return [{cycle["concurrentUsers"]: cycle["page"][page_data_type] for cycle in result["cycles"]} for result in results]

    def _filter_results_with_not_same_concurrent_users(self, concurrent_users, results):
        return_value = []
        for result in results:
            result_concurrent_users = [cycle["concurrentUsers"] for cycle in result["cycles"]]
            if concurrent_users == result_concurrent_users:
                return_value.append(result)

        return return_value

    @tornado.web.asynchronous
    def get(self, team, project, module, class_name, test):
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        kwargs = {
            "version": self.version(),
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
        api_result = self.get_api("results/%s/%s/%s/%s/%s/" % (team, project, module, class_name, test))
        if api_result.status_code == 200 and api_result.content:
            results = loads(api_result.content)
            concurrent_users = self._get_concurrent_users_for_results(results)
            concurrent_users = concurrent_users[0]
            results = self._filter_results_with_not_same_concurrent_users(concurrent_users, results)

            kwargs.update({
                "results": results,
                "apdex_concurrent_users": concurrent_users,
                "apdex_values": self._get_page_values_for("apdex", results),
                "pps_values": self._get_page_values_for("successfulPagesPerSecond", results),
                "average_response_time_values": self._get_page_values_for("average", results),
                "page_concurrent_users": concurrent_users
            })
        self.render('trend.html', **kwargs)
