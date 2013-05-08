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

        team = Team.create(name, owner=self.current_user)

        if team is None:
            self.set_status(409)
            self.finish()
            return

        self.set_status(200)
        self.write("OK")
        self.finish()

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    def put(self, team_name):
        team = Team.objects.filter(name=team_name).first()

        if team is None:
            self.set_status(404)
            self.finish()
            return

        if self.current_user.id != team.owner.id:
            self.set_status(403)
            self.finish()
            return

        put_arguments = parse_qs(self.request.body)
        name = put_arguments.get(six.b("name"), None)
        if not name:
            self.set_status(400)
            self.finish()
            return

        name = name[0]
        if isinstance(name, six.binary_type):
            name = name.decode('utf-8')

        team.name = name
        team.save()

        self.set_status(200)
        self.write("OK")
        self.finish()


class TeamMembersHandler(BaseHandler):

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    def patch(self, team_name):
        team = Team.objects.filter(name=team_name).first()

        if team is None:
            self.set_status(404)
            self.finish()
            return

        if self.current_user.id != team.owner.id:
            self.set_status(403)
            self.finish()
            return

        put_arguments = parse_qs(self.request.body)
        user_email = put_arguments.get(six.b("user"), None)

        if user_email:
            user_email = user_email[0]
            if isinstance(user_email, six.binary_type):
                user_email = user_email.decode('utf-8')

            user = User.objects.filter(email=user_email).first()

            if user is None:
                self.set_status(400)
                self.write("User not found")
                self.finish()
                return

            team.members.append(user)
        else:
            self.set_status(400)
            self.finish()
            return

        team.save()

        self.set_status(200)
        self.write("OK")
        self.finish()
