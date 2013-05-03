#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tornado.web

from wight.api.handlers.base import BaseHandler
from wight.models import User


class AuthenticationHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        email = self.request.headers.get("Email", None)
        password = self.request.headers.get("Password", None)

        if not email or not password:
            self.set_status(400)
            self.finish()
            return

        user = User.authenticate(email, password, expiration=self.application.config.TOKEN_EXPIRATION_IN_MINUTES)

        if user is None:
            self.set_status(403)
            self.finish()
            return

        self.set_status(200)
        self.set_header("Token", user.token)
        self.set_header("Token-Expiration", user.token_expiration.isoformat())
        self.write("OK")
        self.finish()


class AuthenticationWithTokenHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        token = self.request.headers.get("Token", None)

        if not token:
            self.set_status(400)
            self.finish()
            return

        user = User.authenticate_with_token(token, expiration=self.application.config.TOKEN_EXPIRATION_IN_MINUTES)

        if user is None:
            self.set_status(403)
            self.finish()
            return

        self.set_status(200)
        self.set_header("Token", user.token)
        self.set_header("Token-Expiration", user.token_expiration.isoformat())
        self.write("OK")
        self.finish()


class RegisterUserHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self):
        email = self.request.headers.get("Email", None)
        password = self.request.headers.get("Password", None)

        if not email or not password:
            self.set_status(400)
            self.finish()
            return

        user = User.create(email, password)

        if user is None:
            self.set_status(409)
            self.write("User already registered.")
            self.finish()
            return

        user = User.authenticate(email, password)

        self.set_status(200)
        self.write("OK")
        self.set_header("Token", user.token)
        self.set_header("Token-Expiration", user.token_expiration.isoformat())
        self.finish()
