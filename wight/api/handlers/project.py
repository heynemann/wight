#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from json import dumps
try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

import tornado.web
import six

from wight.api.handlers.base import BaseHandler
from wight.models import Team, User


class ProjectHandler(BaseHandler):

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    @BaseHandler.team_member
    def post(self, team):
        name = self.get_argument("name", None)
        if not name:
            self.set_status(400)
            self.finish()
            return

        team.add_project(name=name, created_by=self.current_user)

        self.set_status(200)
        self.write("OK")
        self.finish()
