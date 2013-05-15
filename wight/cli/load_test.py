#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import controller

from wight.cli.base import WightBaseController, ConnectedController


class ScheduleLoadTestController(WightBaseController):
    class Meta:
        label = 'schedule'
        stack_on = 'base'
        description = 'Schedules a new load test.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['team_name'], dict(help='The name of the team that owns the project to schedule a load test')),
            (['project_name'], dict(help='The name of the project to schedule a load test')),
        ]

    @controller.expose(hide=False, aliases=["schedule"], help='Schedules a new load test.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        team_name = self.arguments.team_name
        project_name = self.arguments.project_name

        log_message = "Scheduled a new load test for project '%s%s%s' in team '%s%s%s' at '%s%s%s' target." % (
            self.keyword_color, project_name, self.reset_success,
            self.keyword_color, team_name, self.reset_success,
            self.keyword_color, target, self.reset_success
        )

        with ConnectedController(self):
            response = self.post("/teams/%(team_name)s/projects/%(project_name)s/load_tests/" % {
                "team_name": team_name,
                "project_name": project_name
            })

            self.line_break()

            if response.status_code == 200:
                self.putsuccess(log_message)
            elif response.status_code == 404:
                self.puterror("Project or Team not found at target '%s%s%s'." % (
                    self.keyword_color, target, self.reset_success
                ))

            self.line_break()
