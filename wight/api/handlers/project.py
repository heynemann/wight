#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from mongoengine import DoesNotExist
import six

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

import tornado.web

from wight.api.handlers.base import BaseHandler


class ProjectHandler(BaseHandler):

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    @BaseHandler.team_member
    def post(self, team, project_name):
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

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    @BaseHandler.team_member
    def put(self, team, project_name):
        put_arguments = parse_qs(self.request.body)
        name = put_arguments.get(six.b("name"), None)
        if name:
            name = name[0]
            if isinstance(name, six.binary_type):
                name = name.decode('utf-8')
        repository = put_arguments.get(six.b("repository"), None)
        if repository:
            repository = repository[0]
            if isinstance(repository, six.binary_type):
                repository = repository.decode('utf-8')
        try:
            team.update_project(project_name, name, repository)
            self.set_status(200)
            self.write("OK")
        except DoesNotExist:
            self.set_status(404)
            self.write("Project with name '%s' was not found." % project_name)

        self.finish()
