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

        last_finished = [
            {"uuid": "finished-uuid1", "created": datetime.now().isoformat()[:19], "project": "project1"},
            {"uuid": "finished-uuid2", "created": datetime.now().isoformat()[:19], "project": "project1"},
            {"uuid": "finished-uuid3", "created": datetime.now().isoformat()[:19], "project": "project2"},
            {"uuid": "finished-uuid4", "created": datetime.now().isoformat()[:19], "project": "project4"},
        ]

        scheduled = [
            {"uuid": "scheduled-uuid1", "created": datetime.now().isoformat()[:19], "project": "project1"},
            {"uuid": "scheduled-uuid2", "created": datetime.now().isoformat()[:19], "project": "project1"},
            {"uuid": "scheduled-uuid3", "created": datetime.now().isoformat()[:19], "project": "project1"},
            {"uuid": "scheduled-uuid4", "created": datetime.now().isoformat()[:19], "project": "project1"},
        ]

        team["last_finished"] = last_finished
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
