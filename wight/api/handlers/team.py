#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tornado.web
from json import dumps

from wight.api.handlers.base import BaseHandler
from wight.models import Team


class TeamHandler(BaseHandler):

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    def get(self, name):
        team = Team.objects.filter(name=name).first()

        if team is None:
            self.set_status(404)
            self.finish()
            return

        self.content_type = 'application/json'

        self.write(dumps(team.to_dict()))

        self.finish()

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    def post(self, _):
        name = self.get_argument("name")

        team = Team.create(name)

        if team is None:
            self.set_status(409)
            self.finish()
            return

        self.set_status(200)
        self.write("OK")
        self.finish()
