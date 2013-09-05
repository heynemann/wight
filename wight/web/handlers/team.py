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

        last_finished = []
        for project in team["projects"]:
            load_tests_response = self.get_api("teams/%s/projects/%s/load_tests/?quantity=5" % (team["name"], project["name"]))
            if load_tests_response.status_code == 200:
                last_finished.extend(loads(load_tests_response.content))

        last_finished.sort(key=lambda load_test: load_test["created"])

        scheduled = [
            {"uuid": "scheduled-uuid1", "created": datetime.now().isoformat()[:19], "project": "project1"},
            {"uuid": "scheduled-uuid2", "created": datetime.now().isoformat()[:19], "project": "project1"},
            {"uuid": "scheduled-uuid3", "created": datetime.now().isoformat()[:19], "project": "project1"},
            {"uuid": "scheduled-uuid4", "created": datetime.now().isoformat()[:19], "project": "project1"},
        ]

        team["last_finished"] = last_finished[:5]
        team["scheduled"] = scheduled
        team["projects"][0]["results"] = [
            {"uuid": "project4-uuid1", "created": datetime.now().isoformat()[:19]},
            {"uuid": "project4-uuid2", "created": datetime.now().isoformat()[:19]},
            {"uuid": "project4-uuid3", "created": datetime.now().isoformat()[:19]},
            {"uuid": "project4-uuid4", "created": datetime.now().isoformat()[:19]},

        ]

        kwargs["team"] = team
        self.set_status(200)
        self.render('team.html', **kwargs)
        self.finish()
