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


class TeamPageHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, team):
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        kwargs = {
            "version": self.version(),
            "team": team,
            "format_date": format_date,
            "report_date": report_date,
        }

        team = self.get_api("teams/%s" % team)
        if team.status_code != 200:
            self.render('team.html', **kwargs)
            self.finish()
            return

        team = loads(team.content)

        all_load_tests = []
        for index, project in enumerate(team["projects"]):
            load_tests_response = self.get_api("teams/%s/projects/%s/load_tests/?quantity=30" % (team["name"], project["name"]))
            if load_tests_response.status_code == 200:
                project_load_tests = loads(load_tests_response.content)
                team["projects"][index]["load_tests"] = project_load_tests
                all_load_tests.extend(project_load_tests)

        all_load_tests.sort(key=lambda load_test: load_test["created"])
        running = [test for test in all_load_tests if test["status"] == "Running"]
        finished = [test for test in all_load_tests if test["status"] == "Finished"]
        scheduled = [test for test in all_load_tests if test["status"] == "Scheduled"]
        failed = [test for test in all_load_tests if test["status"] == "Failed"]

        team["finished"] = finished[:9]
        team["scheduled"] = scheduled[:9]
        team["failed"] = failed[:9]
        team["running"] = running[:9]
        kwargs["team"] = team
        self.set_status(200)
        self.render('team.html', **kwargs)
        self.finish()
