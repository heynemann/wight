#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tornado.web

from wight.api.handlers.base import BaseHandler
from wight.models import LoadTest


class LoadTestHandler(BaseHandler):

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    @BaseHandler.team_member
    def post(self, team, project_name):
        project = [project for project in team.projects if project.name.lower().strip() == project_name.lower().strip()] or None
        if not project:
            self.set_status(404)
            self.finish()
            return

        project = project[0]

        try:
            test = LoadTest(scheduled=True, team=team, created_by=self.current_user, project_name=project.name)
            test.save()
        except ValueError:
            self.set_status(409)
            self.finish()

        self.set_status(200)
        self.write("OK")
        self.finish()
