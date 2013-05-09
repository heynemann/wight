#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import controller

from wight.cli.base import WightBaseController, ConnectedController


class AuthController(WightBaseController):
    class Meta:
        label = 'login'
        description = 'Log-in to wight (or register if user not found).'
        config_defaults = dict()

        arguments = [
            (['--email'], dict(help='E-mail to authenticate with.', required=False)),
            (['--password'], dict(help='Password to authenticate with.', required=False)),
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
        ]

    def __abort(self, message="Aborting..."):
        self.line_break()
        self.puterror(message)
        self.line_break()

    @controller.expose(hide=True, help='Log-in to wight (or register if user not found).')
    def default(self):
        if not self.app.user_data or not self.app.user_data.target:
            message = "Wight target not set. Please use '%swight target-set %s<url of target>%s'" + \
                " to specify the api target to be used."

            self.line_break()
            self.puterror(message % (self.commands_color, self.keyword_color, self.reset_error))
            self.line_break()
            return False

        self.log.info("Authenticating with %s." % self.app.user_data.target)

        email = self.arguments.email
        if email is None:
            self.line_break()
            email = self.ask_for("%sPlease enter the %se-mail%s to authenticate with:" % (
                self.reset, self.keyword_color, self.reset)
            )

        if not email:
            self.__abort()
            return False

        password = self.arguments.password
        if password is None:
            password = self.get_pass("%sPlease enter the %spassword%s to authenticate with (nothing will be displayed):" % (
                self.reset, self.keyword_color, self.reset)
            )

        if not password:
            self.__abort()
            return False

        with ConnectedController(self):
            response = self.get("/auth/user", headers={
                'email': email,
                'password': password
            })

            if response.status_code == 400:
                self.__abort("Invalid email or password")
                return False
            if response.status_code == 403:
                self.__abort("Authentication failed.")
                return False
            elif response.status_code == 404:
                register = self.ask_for("%sUser does not exist. Do you wish to register? [%sy/n%s]" % (
                    self.reset, self.keyword_color, self.reset)
                )

                if not register or register.lower() not in ("y", "n") or register.lower() == "n":
                    self.__abort()
                    return False

                response = self.get("/auth/register", headers={
                    'email': email,
                    'password': password
                })

                self.line_break()
                self.putsuccess("User registered and authenticated.")
                self.line_break()
            elif response.status_code == 200:
                self.line_break()
                self.putsuccess("Authenticated.")
                self.line_break()

            self.__update_token(response)
        return True

    def __update_token(self, response):
        token = response.headers.get('Token')
        self.app.user_data.token = token
        self.app.user_data.save()
