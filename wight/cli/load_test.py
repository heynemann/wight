#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from json import loads

from cement.core import controller
from prettytable import PrettyTable

from wight.cli.base import WightBaseController, ConnectedController


class ScheduleLoadTestController(WightBaseController):
    class Meta:
        label = 'schedule'
        stack_on = 'base'
        description = 'Schedules a new load test.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['--base_url'], dict(help='The base url to run the load test against', required=True)),
            (['--team_name'], dict(help='The name of the team that owns the project to schedule a load test', required=True)),
            (['--project_name'], dict(help='The name of the project to schedule a load test', required=True)),
        ]

    @controller.expose(hide=False, aliases=["schedule"], help='Schedules a new load test.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        team_name = self.arguments.team_name
        project_name = self.arguments.project_name
        base_url = self.arguments.base_url

        log_message = "Scheduled a new load test for project '%s%s%s' in team '%s%s%s' at '%s%s%s' target." % (
            self.keyword_color, project_name, self.reset_success,
            self.keyword_color, team_name, self.reset_success,
            self.keyword_color, target, self.reset_success
        )

        with ConnectedController(self):
            response = self.post("/teams/%(team_name)s/projects/%(project_name)s/load_tests/" % {
                "team_name": team_name,
                "project_name": project_name
            }, {
                'base_url': base_url
            })

            self.line_break()

            if response.status_code == 200:
                self.putsuccess(log_message)
            elif response.status_code == 404:
                self.puterror("Project or Team not found at target '%s%s%s'." % (
                    self.keyword_color, target, self.reset_success
                ))

            self.line_break()


class ListLoadTestController(WightBaseController):
    class Meta:
        label = 'list'
        stack_on = 'base'
        description = 'List load tests.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['--team'], dict(help='The name of the team that owns the project to list load tests', required=False)),
            (['--project'], dict(help='The name of the project to list load tests', required=False)),
        ]

    @controller.expose(hide=False, aliases=["list"], help='List a load tests.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        team_name = self.arguments.team
        teams_names = []
        quantity = "3"
        if team_name:
            teams_names.append(team_name)
            quantity = "5"
        else:
            user_info = self.get("/user/info")
            user_info = loads(user_info.content)
            teams_names = [team["name"] for team in user_info["user"]["teams"]]

        project_name = self.arguments.project
        teams_projects = []
        for team_name in teams_names:
            if project_name:
                teams_projects.append((team_name, project_name))
                quantity = "20"
            else:
                team_info = self.get("/teams/%s" % team_name)
                team_info = loads(team_info.content)
                teams_projects.extend([(team_name, project["name"]) for project in team_info["projects"]])

        load_tests = []
        for team_project in teams_projects:
            team, project = team_project
            load_test_info = self.get("/teams/%s/projects/%s/load_tests/?quantity=%s" % (team, project, quantity))
            if load_test_info.status_code == 403:
                target = self.app.user_data.target
                self.puterror(
                    "Your are not the owner or team member for the team '%s%s%s' and cannot list its tests in target '%s%s%s'." % (
                        self.keyword_color, team, self.reset_error,
                        self.keyword_color, target, self.reset_error
                    ))
                return
            load_tests.append({"header": team_project, "load_tests": loads(load_test_info.content)})

        self.__print_load_tests(load_tests)

    def __print_load_tests(self, load_tests):
        for load_test in load_tests:
            self.line_break()
            self.write("%sTeam%s: %s%s%s ---- %sProject%s: %s%s%s" % (
                self.title_color, self.reset,
                self.keyword_color, load_test["header"][0], self.reset,
                self.title_color, self.reset,
                self.keyword_color, load_test["header"][1], self.reset,
            ))
            headers = [
                "%suuid%s" % (self.commands_color, self.reset),
                "%sstatus%s" % (self.commands_color, self.reset),
                ""
            ]
            table = PrettyTable(headers)
            table.align[headers[0]] = "l"
            table.align[headers[2]] = "l"

            for test in load_test["load_tests"]:
                table.add_row([test["uuid"], test["status"], "wight show %s" % test["uuid"]])
            self.puts(table)
