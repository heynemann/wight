#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import six
from json import loads
from cement.core import controller
from prettytable import PrettyTable

from wight.cli.base import WightBaseController, connected_controller


class ShowUserController(WightBaseController):
    class Meta:
        label = 'user-info'
        stack_on = 'base'
        description = 'Shows user info'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
        ]

    @controller.expose(hide=False, aliases=["user-info"], help='Show user info.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        with connected_controller(self):
            response = self.get("/user/info")
            if response.status_code == 200:
                content = response.content
                if isinstance(content, six.binary_type):
                    content = content.decode('utf-8')
                content = loads(content)
                self.write("User: %s" % content['user']['email'])
                members_table = PrettyTable(["team", "role"])
                members_table.align["team"] = "l"
                members_table.align["role"] = "l"
                for team in content['user']['teams']:
                    members_table.add_row([team['name'], team['role']])
                self.write(members_table)
            elif response.status_code == 401:
                self.write("User not logged in. Run wight authenticate")


class ChangePasswordController(WightBaseController):

    class Meta:
        label = 'change-password'
        stack_on = 'base'
        description = 'Change user password'

    @controller.expose(hide=False, aliases=["change-password"], help='Changes user password.')
    @WightBaseController.authenticated
    def default(self):
        self.line_break()
        old_pass = self.get_pass("Please enter your current password:")
        self.line_break()
        new_pass = self.get_pass("Please enter your new password:")
        self.line_break()
        new_pass_check = self.get_pass("Please enter your new password again:")

        if new_pass != new_pass_check:
            self.line_break()
            self.puterror("New password check failed. Please try again.")
            self.line_break()
            return

        with connected_controller(self):
            response = self.post("/user/change-pass", data={"old_pass": old_pass, "new_pass": new_pass})

            if response.status_code == 403:
                self.line_break()
                self.puterror("The original password didn't match. Please try again")
                self.line_break()
            elif response.status_code == 200:
                self.line_break()
                self.puts("Password changed successfuly.")
                self.line_break()
            else:
                self.line_break()
                self.puterror("Wight API returned an unexpected status code!")
                self.line_break()
