#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import controller

from wight.cli.base import WightBaseController


class GetDefaultController(WightBaseController):
    class Meta:
        label = 'default-get'
        stack_on = 'base'
        description = 'Shows the defined default team and/or project.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
        ]

    @controller.expose(hide=False, aliases=["default-get"], help='Shows the defined default team and/or project.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        user_data = self.app.user_data
        team_msg = "Default team not set."
        project_msg = "Default project not set."
        if hasattr(user_data, 'team'):
            team_msg = "Default team is '%s%s%s'." % (self.keyword_color, user_data.team, self.reset_success)
        if hasattr(user_data, 'project'):
            project_msg = "Default project is '%s%s%s'." % (self.keyword_color, user_data.project, self.reset_success)

        self.line_break()
        self.write(team_msg)
        self.line_break()
        self.write(project_msg)
        self.line_break()


class SetDefaultController(WightBaseController):
    class Meta:
        label = 'default-set'
        stack_on = 'base'
        description = 'Define default team and/or project to be used in subsequent commands.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['--team'], dict(help='The name of the team to be used as default', required=False)),
            (['--project'], dict(help='The name of the project to be used as default', required=False)),
        ]

    @controller.expose(hide=False, aliases=["default-set"], help='Define default team and/or project to be used in subsequent commands.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        team = self.arguments.team
        project = self.arguments.project
        self.app.user_data.set_default(team=team, project=project)
        self.app.user_data.save()

        team_msg = "Default team not set."
        project_msg = "Default project not set."
        if team:
            team_msg = "Default team set to '%s%s%s'." % (self.keyword_color, team, self.reset_success)
        if project:
            project_msg = "Default project set to '%s%s%s'." % (self.keyword_color, project, self.reset_success)

        self.line_break()
        self.putsuccess(team_msg)
        self.line_break()
        self.putsuccess(project_msg)
        self.line_break()
