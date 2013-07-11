#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys
import time
from json import loads
from datetime import datetime

import six
from cement.core import controller
from cement.core.exc import CaughtSignal
from prettytable import PrettyTable
from dateutil import tz

from wight.cli.base import WightBaseController, connected_controller


def get_local_time_from_utc(utc_date):
    utc_date = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%S")
    local_tz = tz.tzlocal()
    utc_tz = tz.gettz('UTC')
    return utc_date.replace(tzinfo=utc_tz).astimezone(local_tz)


class ScheduleLoadTestController(WightBaseController):
    class Meta:
        label = 'schedule'
        stack_on = 'base'
        description = 'Schedules a new load test.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['--url'], dict(help='The base url to run the load test against', required=True)),
            (['--team'], dict(help='The name of the team that owns the project to schedule a load test', required=True)),
            (['--project'], dict(help='The name of the project to schedule a load test', required=True)),
        ]

    @controller.expose(hide=False, aliases=["schedule"], help='Schedules a new load test.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        team_name = self.arguments.team
        project_name = self.arguments.project
        base_url = self.arguments.url

        log_message = "Scheduled a new load test for project '%s%s%s' in team '%s%s%s' at '%s%s%s' target." % (
            self.keyword_color, project_name, self.reset_success,
            self.keyword_color, team_name, self.reset_success,
            self.keyword_color, target, self.reset_success
        )

        with connected_controller(self):
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
        with connected_controller(self):
            if team_name:
                teams_names.append(team_name)
            else:
                user_info = self.get("/user/info")
                user_info = loads(user_info.content)
                teams_names = [team["name"] for team in user_info["user"]["teams"]]

            project_name = self.arguments.project
            teams_and_projects = self.__get_teams_and_projects_names(project_name, team_name, teams_names)
            load_tests = []
            quantity = self.__define_quantity(team_name, project_name)
            for team_and_project in teams_and_projects:
                team, project = team_and_project
                load_test_info = self.get("/teams/%s/projects/%s/load_tests/?quantity=%s" % (team, project, quantity))
                if load_test_info.status_code == 403:
                    self.puterror(
                        "You are not the owner or a team member for '%s%s%s' and thus can't list its tests in target '%s%s%s'." % (
                            self.keyword_color, team, self.reset_error,
                            self.keyword_color, self.app.user_data.target, self.reset_error
                        ))
                    return
                load_tests.append({"header": team_and_project, "load_tests": loads(load_test_info.content)})

            self.__print_load_tests(load_tests)

    def __get_teams_and_projects_names(self, project_name, team_name, teams_names):
        teams_projects = []
        if project_name and team_name:
            teams_projects.append((team_name, project_name))
        else:
            for name in teams_names:
                team_info = self.get("/teams/%s" % name)
                team_info = loads(team_info.content)
                teams_projects.extend([
                    (name, project["name"])
                    for project in team_info["projects"]
                    if not project_name or project_name == project["name"]
                ])
        return teams_projects

    def __define_quantity(self, team_name, project_name):
        if project_name:
            return "20"
        if team_name:
            return "5"
        return "3"

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
                "%ssince%s" % (self.commands_color, self.reset),
                ""
            ]
            table = PrettyTable(headers)
            table.align[headers[0]] = "l"

            spacer = "         -         "
            for test in load_test["load_tests"]:
                dt = test['created'] if test["status"] == "Scheduled" else test["lastModified"]
                dt = get_local_time_from_utc(dt)

                if test["status"] == "Running":
                    actual_date = datetime.strptime(test['lastModified'], "%Y-%m-%dT%H:%M:%S")
                    dt = "%s (%.2fs)" % (dt, (datetime.utcnow() - actual_date).total_seconds())

                table.add_row(
                    [
                        test["uuid"],
                        self.get_colored_status(test["status"]),
                        dt if test["status"] in ["Scheduled", "Running"] else spacer,
                        "%swight show %s%s" % (self.commands_color, test["uuid"], self.reset)
                    ]
                )

            self.puts(table)
            self.line_break()

    def get_colored_status(self, status):
        color = self.text_color

        if status == "Finished":
            color = self.success_text_color

        if status == "Failed":
            color = self.error_text_color

        if status == "Running":
            color = self.commands_color

        return "%s%s%s" % (
            color, status, self.reset
        )


class InstanceLoadTestController(WightBaseController):
    class Meta:
        label = 'show'
        stack_on = 'base'
        description = 'Show load tests.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['--track'], dict(help='Keep pinging the server until the test is finished.', action="store_true", default=False, required=False)),
            (['load_test_uuid'], dict(help='Load test uuid')),
        ]

    @controller.expose(hide=False, aliases=["show"], help='Show load tests.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        with connected_controller(self):
            content = self._load_response()

            while self.arguments.track and (content['status'] == "Running" or content['status'] == "Scheduled"):
                try:
                    time.sleep(5)
                    self.line_break()
                    self.write("-" * 80)
                    content = self._load_response()
                except KeyboardInterrupt:
                    sys.exit(1)
                except CaughtSignal:
                    sys.exit(1)

    def _load_response(self):

        url = '/load_tests/%s' % self.arguments.load_test_uuid

        response = self.get(url)

        if response.status_code == 404:
            return self.write("Load test %s doesn't exist" % self.arguments.load_test_uuid)

        content = response.content
        if isinstance(content, six.binary_type):
            content = content.decode('utf-8')
        content = loads(content)

        for result in content['results']:
            result['requests_per_second'] = round(result['requests_per_second'], 2)
            result['p95'] = round(result['p95'], 2)

        self._print_response(content)

        return content

    def _print_response(self, load_test):
        self.line_break()

        self.write("%sLoad test%s: %s%s%s" % (
            self.title_color, self.reset,
            self.keyword_color, load_test["uuid"], self.reset,
        ))
        self.write("%sStatus%s: %s%s%s" % (
            self.title_color, self.reset,
            self.keyword_color, load_test["status"], self.reset,
        ))

        if "lastCommit" in load_test and load_test['lastCommit'] is not None:
            self.write("%sBased on commit%s: %s%s%s by %s%s%s" % (
                self.title_color, self.reset,
                self.keyword_color, load_test["lastCommit"]["hex"], self.reset,
                self.keyword_color, load_test["lastCommit"]["committer"]["name"], self.reset,
            ))

        if load_test['status'] == "Failed":
            self.puterror("This test run failed because:")
            self.line_break()
            self.write(load_test['error'])
            self.line_break()
            return

        if load_test["status"] == "Running":
            dt = get_local_time_from_utc(load_test['lastModified'])
            actual_date = datetime.strptime(load_test['lastModified'], "%Y-%m-%dT%H:%M:%S")
            dt = "%s (%.2fs)" % (dt, (datetime.utcnow() - actual_date).total_seconds())

            self.write("%sRunning since%s: %s%s%s" % (
                self.title_color, self.reset,
                self.keyword_color, dt, self.reset,
            ))

        if load_test["status"] == "Scheduled":
            dt = load_test['created'].replace('T', ' ')
            actual_date = datetime.strptime(load_test['created'], "%Y-%m-%dT%H:%M:%S")
            dt = "%s (%.2fs)" % (dt, (datetime.utcnow() - actual_date).total_seconds())

            self.write("%sScheduled since%s: %s%s%s" % (
                self.title_color, self.reset,
                self.keyword_color, dt, self.reset,
            ))

        self.line_break()

        if load_test['results']:
            headers = ['title', 'concurrent users', 'rps', 'p95', 'failed']
            keys = ['title', 'concurrent_users', 'requests_per_second', 'p95', 'failed_requests']

            table = PrettyTable(headers + [''])

            for result in load_test['results']:
                row = []
                for index, header in enumerate(headers):
                    row.append(result[keys[index]])
                row.append("%swight show-result %s%s" % (self.commands_color, result['uuid'], self.reset))
                table.add_row(row)

            self.write(table)

            line = str(table).split('\n')[0]

            msg = "rps means requests per second, p95 means the 95 percentile in seconds and failed means request errors"
            msg = self.align_right(msg, len(line))
            msg = msg.replace("rps", "%srps%s" % (self.commands_color, self.reset))
            msg = msg.replace("p95", "%sp95%s" % (self.commands_color, self.reset))
            msg = msg.replace("failed", "%sfailed%s" % (self.commands_color, self.reset))
            self.write("%s%s%s" % (self.comment_color, msg, self.reset))
            self.line_break()
        else:
            self.puterror("No test results yet.")
            self.line_break()


class ShowResultController(WightBaseController):
    class Meta:
        label = 'show-result'
        stack_on = 'base'
        description = 'Show load test results.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            #(['--team'], dict(help='The name of the team that owns the project load tests', required=True)),
            #(['--project'], dict(help='The name of the project load tests', required=True)),
            (['load_test_uuid'], dict(help='Load test uuid')),
        ]

    @controller.expose(hide=False, aliases=["show-result"], help='Show load-test result.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        with connected_controller(self):
            url = '/load_tests/%s/results/' % self.arguments.load_test_uuid

            response = self.get(url)

            if response.status_code == 404:
                return self.write("Load test %s doesn't exist" % self.arguments.load_test_uuid)

            content = response.content
            if isinstance(content, six.binary_type):
                content = content.decode('utf-8')
            content = loads(content)
            self._print_response(content)

    def _print_two_columns(self, first_title, first_value, second_title, second_value):
        self.write(("%s%s%s: %s%-" + str(50 - len(first_title)) + "s%s %s%s%s: %s%ss%s") % (
            self.keyword_color, first_title.strip(), self.reset,
            self.commands_color, str(first_value).strip(), self.reset,
            self.keyword_color, second_title.strip(), self.reset,
            self.commands_color, str(second_value).strip(), self.reset,
        ))

    def _print_response(self, load_test):
        result = [result for result in load_test['results'] if result['uuid'] == self.arguments.load_test_uuid]

        if not result:
            self.write("Result with UUID %s was not found!" % self.argument.load_test_uuid)

        result = result[0]

        self.line_break()

        self.write("%sLoad test%s: %s%s%s" % (
            self.title_color, self.reset,
            self.keyword_color, load_test["uuid"], self.reset,
        ))
        self.write("%sStatus%s: %s%s%s" % (
            self.title_color, self.reset,
            self.keyword_color, load_test["status"], self.reset,
        ))

        self.write("%sWeb Report URL%s: %s%s%s" % (
            self.title_color, self.reset,
            self.keyword_color, load_test['reportURL'], self.reset,
        ))

        self.line_break()
        self.write("%sBench Configuration%s" % (
            self.title_color, self.reset
        ))
        self.write('-' * len('Bench Configuration'))

        cfg = result['config']
        test_name = "%s.%s" % (cfg['className'], cfg['testName'])
        items = (
            ("Title", cfg['title'], 'Description', cfg['description']),
            ("Module", cfg['module'], "Test", test_name),
            ("Cycles", cfg['cycles'], "Cycle Duration", cfg['cycleDuration']),
            ("Base URL", cfg['targetServer'], "Test Date", cfg['testDate']),
        )

        for item in items:
            self._print_two_columns(*item)

        headers = ['users', 'requests', 'error %', 'rps', 'minimum', 'average', 'p90', 'p95', 'maximum']
        table = PrettyTable(["%s%s%s" % (self.keyword_color, header, self.reset) for header in headers])

        for cycle in sorted(result['cycles'], key=lambda item: item['cycleNumber']):
            req = cycle['request']
            row = [
                cycle['concurrentUsers'],
                req['successfulRequests'],
                "%.2f%%" % req['failedRequestPercentage'],
                "%.2f" % req['successfulRequestsPerSecond'],
                "%.2fs" % req['minimum'],
                "%.2fs" % req['average'],
                "%.2fs" % req['p90'],
                "%.2fs" % req['p95'],
                "%.2fs" % req['maximum']
            ]
            table.add_row(row)

        self.line_break()
        self.write(table)
        line = str(table).split('\n')[0]

        msg = "rps means requests per second and average, p95 and maximum are all response time in seconds"
        msg = self.align_right(msg, len(line))
        self.write("%s%s%s" % (self.comment_color, msg, self.reset))
        self.line_break()

        #headers = ['title', 'concurrent users', 'rps', 'p95', 'failed']
        #keys = ['title', 'concurrent_users', 'requests_per_second', 'p95', 'failed_requests']

        #table = PrettyTable(headers + [''])

        #for result in load_test['results']:
            #row = []
            #for index, header in enumerate(headers):
                #row.append(result[keys[index]])
            #row.append("%swight show-result %s%s" % (self.commands_color, result['uuid'], self.reset))
            #table.add_row(row)

        #self.write(table)

        #line = str(table).split('\n')[0]


