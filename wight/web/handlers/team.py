#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from datetime import datetime

import tornado.web

from wight.web.handlers.base import BaseHandler, format_date


class TeamPageHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, team):
        self.set_status(200)
        report_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        kwargs = {
            "version": self.version(),
            "team": team,
            "format_date": format_date,
            "report_date": report_date,
        }
        if team == "nada":
            self.render('team.html', **kwargs)
            self.finish()

        last_finished = [
            {"uuid": "finished-uuid1", "created": datetime.now().isoformat()[:19]},
            {"uuid": "finished-uuid2", "created": datetime.now().isoformat()[:19]},
            {"uuid": "finished-uuid3", "created": datetime.now().isoformat()[:19]},
            {"uuid": "finished-uuid4", "created": datetime.now().isoformat()[:19]},
        ]

        scheduled = [
            {"uuid": "scheduled-uuid1", "created": datetime.now().isoformat()[:19]},
            {"uuid": "scheduled-uuid2", "created": datetime.now().isoformat()[:19]},
            {"uuid": "scheduled-uuid3", "created": datetime.now().isoformat()[:19]},
            {"uuid": "scheduled-uuid4", "created": datetime.now().isoformat()[:19]},
        ]

        projects = [
            {
                "name": "project1",
                "results": [
                    {"uuid": "project1-uuid1", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project1-uuid2", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project1-uuid3", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project1-uuid4", "created": datetime.now().isoformat()[:19]},

                ]
            },
            {
                "name": "project2",
                "results": [
                    {"uuid": "project2-uuid1", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project2-uuid2", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project2-uuid3", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project2-uuid4", "created": datetime.now().isoformat()[:19]},

                ]
            },
            {
                "name": "project3",
                "results": [
                    {"uuid": "project3-uuid1", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project3-uuid2", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project3-uuid3", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project3-uuid4", "created": datetime.now().isoformat()[:19]},

                ]
            },
            {
                "name": "project4",
                "results": [
                    {"uuid": "project4-uuid1", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project4-uuid2", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project4-uuid3", "created": datetime.now().isoformat()[:19]},
                    {"uuid": "project4-uuid4", "created": datetime.now().isoformat()[:19]},

                ]
            }
        ]

        team = {
            "name": "AppDev",
            "last_finished": last_finished,
            "scheduled": scheduled,
            "projects": projects
        }
        kwargs["team"] = team
        self.render('team.html', **kwargs)
        self.finish()
