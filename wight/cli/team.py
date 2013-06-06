#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from json import loads

import six

from cement.core import controller
from prettytable import PrettyTable

from wight.cli.base import WightBaseController, connected_controller


class CreateTeamController(WightBaseController):
    class Meta:
        label = 'team-create'
        stack_on = 'base'
        description = 'Create a team.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team to be created')),
        ]

    @controller.expose(hide=False, aliases=["team-create"], help='Create a team.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name

        log_message = "Created '%s%s%s' team in '%s%s%s' target." % (
            self.keyword_color, name, self.reset_success,
            self.keyword_color, target, self.reset_success
        )

        with connected_controller(self):
            response = self.post("/teams", {"name": name})

            self.line_break()

            if response.status_code == 200:
                self.putsuccess(log_message)
            elif response.status_code == 409:
                self.puterror("The team '%s%s%s' already exists in target '%s%s%s'." % (
                    self.keyword_color, name, self.reset_error,
                    self.keyword_color, target, self.reset_error
                ))
            elif response.status_code == 400:
                self.puterror("You should define a name for the team to be created.")

            self.line_break()


class ShowTeamController(WightBaseController):
    class Meta:
        label = 'team-show'
        stack_on = 'base'
        description = 'Show the registered team information.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team to be showed')),
        ]

    def __print_members(self, owner, members):
        headers = [
            "%suser%s" % (self.commands_color, self.reset),
            "%srole%s" % (self.commands_color, self.reset)
        ]
        members_table = PrettyTable(headers)

        members_table.align[headers[0]] = "l"
        members_table.align[headers[1]] = "l"
        members_table.add_row([owner, "owner"])
        for member in members:
            members_table.add_row([member, "member"])
        self.puts(members_table)

    def __print_projects(self, projects):
        headers = [
            "%sproject name%s" % (self.commands_color, self.reset),
            "%srepository%s" % (self.commands_color, self.reset),
            "%screated by%s" % (self.commands_color, self.reset)
        ]
        members_table = PrettyTable(headers)

        members_table.align[headers[0]] = "l"
        members_table.align[headers[1]] = "l"
        members_table.align[headers[2]] = "l"

        for project in projects:
            members_table.add_row([project['name'], project['repository'], project['createdBy']])
        self.puts(members_table)

    @controller.expose(hide=False, aliases=["team-show"], help='Show the registered team information.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        with connected_controller(self):
            response = self.get("/teams/%s" % name)
            if response.status_code == 200:
                self.line_break()
                self.puts("%s%s" % (self.title_color, name))
                self.puts("-" * len(name))
                self.line_break()

                content = response.content
                if isinstance(content, six.binary_type):
                    content = content.decode('utf-8')
                team_data = loads(content)

                self.__print_members(team_data['owner'], team_data['members'])

                self.line_break()
                if 'projects' in team_data and team_data['projects']:
                    self.__print_projects(team_data['projects'])
                else:
                    self.puterror("This team has no projects. To create a project use '%swight project-create%s'." % (
                        self.commands_color, self.reset_error
                    ))

                self.line_break()
            elif response.status_code == 404:
                self.line_break()
                self.puterror("The team '%s%s%s' does not exists in target '%s%s%s'." % (
                    self.keyword_color, name, self.reset_error,
                    self.keyword_color, target, self.reset_error)
                )
                self.line_break()


class UpdateTeamController(WightBaseController):
    class Meta:
        label = 'team-update'
        stack_on = 'base'
        description = 'Updates a team.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team')),
            (['new_name'], dict(help='The new name for the team')),
        ]

    @controller.expose(hide=False, aliases=["team-update"], help='Updates a team.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        new_name = self.arguments.new_name
        log_message = "Updated '%s%s%s' team to '%s%s%s' in '%s%s%s' target." % (
            self.keyword_color, name, self.reset_success,
            self.keyword_color, new_name, self.reset_success,
            self.keyword_color, target, self.reset_success
        )

        with connected_controller(self):
            response = self.put("/teams/%s" % name, {"name": new_name})

            self.line_break()
            if response.status_code == 200:
                self.putsuccess(log_message)
            elif response.status_code == 403:
                self.puterror("You are not the owner of team '%s%s%s' in target '%s%s%s' (which means you can't update it)." % (
                    self.keyword_color, name, self.reset_error,
                    self.keyword_color, target, self.reset_error
                ))
            elif response.status_code == 404:
                self.puterror("Team '%s%s%s' does not exist in target '%s%s%s'." % (
                    self.keyword_color, name, self.reset_error,
                    self.keyword_color, target, self.reset_error
                ))
            elif response.status_code == 400:
                self.puterror("The team's new name can't be null or empty.")
            self.line_break()


class DeleteTeamController(WightBaseController):
    class Meta:
        label = 'team-delete'
        stack_on = 'base'
        description = 'Delete a team.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team to be deleted')),
        ]

    @controller.expose(hide=False, aliases=["team-delete"], help='Delete a team.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        self.write("")
        self.write("This operation will delete all projects and all tests of team '%s'." % name)
        self.write("You have to retype the team name to confirm deletion.")
        self.write("")
        name_confirmation = self.ask_for("Team name: ")
        if name_confirmation != name:
            self.write("The team name you type ('%s') is not the same you pass ('%s')." % (name, name_confirmation))
            self.write("Operation aborted...")
            return
        log_message = "Deleted '%s' team, all its projects and tests in '%s' target." % (name, target)
        with connected_controller(self):
            response = self.delete("/teams/%s" % name)
            if response.status_code == 200:
                self.log.info(log_message)
                self.write(log_message)
            elif response.status_code == 403:
                self.write("You are not the owner of team '%s' in target '%s' (which means you can't delete it)." % (name, target))
            elif response.status_code == 404:
                self.write("Team '%s' does not exist in target '%s'." % (name, target))


class TeamAddUserController(WightBaseController):
    class Meta:
        label = 'team-adduser'
        stack_on = 'base'
        description = 'Adds user to a team'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team')),
            (['user_email'], dict(help='User to be added')),
        ]

    @controller.expose(hide=False, aliases=["team-adduser"], help='Adds user to a team.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        user_email = self.arguments.user_email

        with connected_controller(self):
            response = self.patch("/teams/%s/members" % name, {"user": user_email})

            self.line_break()

            if response.status_code == 200:
                self.putsuccess("User '%s%s%s' added to Team '%s%s%s'." % (
                    self.keyword_color, user_email, self.reset_success,
                    self.keyword_color, name, self.reset_success
                ))
            elif response.status_code == 403:
                self.puterror("You are not authenticated. Please use '%swight login%s'." % (
                    self.commands_color, self.reset_error
                ))
            elif response.status_code == 404:
                self.puterror("Team '%s%s%s' does not exist in target '%s%s%s'." % (
                    self.keyword_color, name, self.reset_error,
                    self.keyword_color, target, self.reset_error
                ))
            elif response.status_code == 401:
                self.puterror("You need to be the team owner or member to add users.")
            elif response.status_code == 409:
                self.puterror(response.content)

            self.line_break()


class TeamRemoveUserController(WightBaseController):
    class Meta:
        label = 'team-removeuser'
        stack_on = 'base'
        description = 'Removess user from a team'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team')),
            (['user_email'], dict(help='User to be removed')),
        ]

    @controller.expose(hide=False, aliases=["team-removeuser"], help='Removess user from a team.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        name = self.arguments.team_name
        user_email = self.arguments.user_email

        with connected_controller(self):
            response = self.delete("/teams/%s/members" % name, {"user": user_email})

            self.line_break()

            if response.status_code == 200:
                self.putsuccess("User '%s%s%s' removed from Team '%s%s%s'." % (
                    self.keyword_color, user_email, self.reset_success,
                    self.keyword_color, name, self.reset_success
                ))
            elif response.status_code == 403:
                self.puterror("You are not authenticated. Please use '%swight login%s'." % (
                    self.commands_color, self.reset_error
                ))
            elif response.status_code == 404:
                self.puterror("Team '%s%s%s' does not exist in target '%s%s%s'." % (
                    self.keyword_color, name, self.reset_error,
                    self.keyword_color, target, self.reset_error
                ))
            elif response.status_code == 401:
                self.puterror("You need to be the team owner or member to remove users.")

            self.line_break()
