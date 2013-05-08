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
from mongoengine import Q


class UserHandler(BaseHandler):

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    def get(self, name):
        user = {'user': {'email': self.current_user.email, 'teams': []}}
        teams = Team.objects(Q(members__contains=self.current_user) | Q(owner=self.current_user))

        for team in teams:
            role = 'owner' if team.owner == self.current_user else 'member'
            user['user']['teams'].append({'name': team.name, 'role': role})

        self.content_type = 'application/json'
        self.write(dumps(user))
        self.finish()
