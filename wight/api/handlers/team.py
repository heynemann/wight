#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tornado.web

from wight.api.handlers.base import BaseHandler
from wight.models import Team


class TeamHandler(BaseHandler):

    @tornado.web.asynchronous
    def post(self):
        name = self.get_argument("name")

        team = Team.create(name)

        if team is None:
            self.set_status(403)
            self.finish()
            return

        self.set_status(200)
        self.write("OK")
        self.finish()
