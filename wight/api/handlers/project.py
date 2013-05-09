#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tornado.web

from wight.api.handlers.base import BaseHandler


class ProjectHandler(BaseHandler):

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    @BaseHandler.team_member
    def post(self, team):
        name = self.get_argument("name", None)
        repository = self.get_argument("repository", None)
        if not name or not repository:
            self.set_status(400)
            self.finish()
            return

        try:
            team.add_project(name=name, repository=repository, created_by=self.current_user)
        except ValueError:
            self.set_status(409)
            self.finish()

        self.set_status(200)
        self.write("OK")
        self.finish()
