#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import controller

from wight.cli.base import WightBaseController, ConnectedController


class CreateProjectController(WightBaseController):
    class Meta:
        label = 'project-create'
        stack_on = 'base'
        description = 'Creates a project.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['--team'], dict(help='Name of the team that owns this project.', required=True)),
            (['--project_name'], dict(help='Name of the project.', required=True)),
            (['--repo'], dict(help='Git repository for this project.', required=True)),
        ]

    @controller.expose(hide=False, aliases=["project-create"], help='Creates a project.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        team_name = self.arguments.team
        name = self.arguments.project_name
        repo = self.arguments.repo

        log_message = "Created '%s' project in '%s' team at '%s'." % (name, team_name, target)
        with ConnectedController(self):
            response = self.post("/teams/%s/projects/" % team_name, {"name": name, "repository": repo})
            if response.status_code == 200:
                self.log.info(log_message)
                self.write(log_message)
                return
            elif response.status_code == 409:
                self.write("The project '%s' already exists in team '%s' at '%s'." % (name, team_name, target))
                return
            elif response.status_code == 400:
                self.write("Both name and repository are required in order to save a team.")
                return

            self.write("The project '%s' was not created! (API Result: '%s', Status Code: '%s'" % (name, response.content, response.status_code))


class UpdateProjectController(WightBaseController):
    class Meta:
        label = 'project-update'
        stack_on = 'base'
        description = 'Updates a project.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['--team'], dict(help='Name of the team that owns this project.', required=True)),
            (['--project'], dict(help='Name of the project to be updated.', required=True)),
            (['--project_name'], dict(help='Name to update for this project', required=False)),
            (['--repo'], dict(help='Git repository to update for this project.', required=False)),
        ]

    @controller.expose(hide=False, aliases=["project-update"], help='Updates a project.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        team_name = self.arguments.team
        project_name = self.arguments.project
        name = self.arguments.project_name
        repo = self.arguments.repo

        with ConnectedController(self):
            response = self.put("/teams/%s/projects/%s" % (team_name, project_name), {"name": name, "repository": repo})
            self.line_break()
            if response.status_code == 200:
                name = name or project_name
                self.putsuccess("Updated '%s%s%s' project in '%s%s%s' team at '%s%s%s'." % (
                    self.keyword_color, name, self.reset_success,
                    self.keyword_color, team_name, self.reset_success,
                    self.keyword_color, target, self.reset_success
                ))
            elif response.status_code == 403:
                self.puterror(
                    "You are not member of the team for the project '%s%s%s' and cannot update it." % (
                        self.keyword_color, project_name, self.reset_error,
                    )
                )
            elif response.status_code == 404:
                self.puterror(
                    "The team '%s%s%s' or the project '%s%s%s' does not exists in target '%s%s%s'." % (
                        self.keyword_color, team_name, self.reset_error,
                        self.keyword_color, project_name, self.reset_error,
                        self.keyword_color, target, self.reset_error
                    )
                )
            self.line_break()


class DeleteProjectController(WightBaseController):
    class Meta:
        label = 'project-delete'
        stack_on = 'base'
        description = 'Deletes a project.'
        config_defaults = dict()

        arguments = [
            (['--conf'], dict(help='Configuration file path.', default=None, required=False)),
            (['--team'], dict(help='Name of the team that owns this project.', required=True)),
            (['--project'], dict(help='Name of the project to be deleted.', required=True)),
        ]

    @controller.expose(hide=False, aliases=["project-delete"], help='Deletes a project.')
    @WightBaseController.authenticated
    def default(self):
        self.load_conf()
        target = self.app.user_data.target
        team_name = self.arguments.team
        project_name = self.arguments.project

        self.line_break()
        self.write("This operation will delete all tests of the project '%s'." % project_name)
        confirmation = self.ask_for("%sAre you sure you want to delete project '%s%s%s'? [%sy/n%s]" % (
            self.reset, self.keyword_color, project_name, self.reset_error, self.keyword_color, self.reset)
        )
        self.line_break()
        if not confirmation or confirmation.lower() not in ("y", "n") or confirmation.lower() == "n":
            self.abort()
            return False
        log_message = "Deleted '%s%s%s' project and tests for team '%s%s%s' in '%s%s%s' target." % (
            self.keyword_color, project_name, self.reset_error,
            self.keyword_color, team_name, self.reset_error,
            self.keyword_color, target, self.reset_error
        )
        with ConnectedController(self):
            response = self.delete("/teams/%s/projects/%s" % (team_name, project_name))
            self.line_break()
            if response.status_code == 200:
                self.log.info(log_message)
                self.write(log_message)
            elif response.status_code == 403:
                self.puterror(
                    "You are not member of the team for the project '%s%s%s' and cannot delete it." % (
                        self.keyword_color, project_name, self.reset_error,
                    )
                )
            self.line_break()
