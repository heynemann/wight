#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import controller

from wight.cli.base import WightBaseController


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

    @controller.expose(hide=True, help='Log-in to wight (or register if user not found).')
    def default(self):
        self.log.info("Authenticating with %s." % self.app.user_data.target)

        email = self.arguments.email
        if email is None:
            email = self.ask_for("Please enter the e-mail to authenticate with:")

        if email is None:
            print("Aborting...")
            return False

        password = self.arguments.password
        if password is None:
            password = self.get_pass("Please enter the password to authenticate with (nothing will be displayed):")

        if password is None:
            print("Aborting...")
            return False

        response = self.api("/auth/user", headers={
            'email': email,
            'password': password
        })

        if response.status_code == 403:
            print("Authentication failed.")
            return False
        elif response.status_code == 404:
            register = self.ask_for("User does not exist. Do you wish to register? [y/n]")
            if not register or register.lower() not in ("y", "n") or register.lower() == "n":
                print("Aborting...")
                return False

            response = self.api("/auth/register", headers={
                'email': email,
                'password': password
            })

            print("User registered and authenticated.")
        elif response.status_code == 200:
            print("Authenticated.")

        self.__update_token(response)
        return True

    def __update_token(self, response):
        token = response.headers.get('Token')
        self.app.user_data.token = token
        self.app.user_data.save()
