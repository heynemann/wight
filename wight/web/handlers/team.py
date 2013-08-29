#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tornado.web

from wight.web.handlers.base import BaseHandler


class TeamPageHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, team):
        self.set_status(200)
        kwargs = {
            "version": self.version(),
            "team": team,
        }
        self.render('team.html', **kwargs)
        self.finish()
