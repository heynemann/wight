#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import UserData
from tests.acceptance.base import AcceptanceTest


class TestDefault(AcceptanceTest):

    team = "team-blah"
    project = "project-blah"

    def test_can_set_team(self):
        result = self.execute("default-set", team=self.team)
        expected = "Default team set to '%s'. Default project not set." % self.team
        expect(result).to_be_like(expected)
        ud = UserData.load()
        expect(ud.team).to_be_like(self.team)

    def test_can_set_project(self):
        result = self.execute("default-set", project=self.project)
        expected = "Default team not set. Default project set to '%s'." % self.project
        expect(result).to_be_like(expected)
        ud = UserData.load()
        expect(ud.project).to_be_like(self.project)

    def test_can_set_team_and_project(self):
        result = self.execute("default-set", team=self.team, project=self.project)
        expected = "Default team set to '%s'. Default project set to '%s'." % (self.team, self.project)
        expect(result).to_be_like(expected)
        ud = UserData.load()
        expect(ud.team).to_be_like(self.team)
        expect(ud.project).to_be_like(self.project)

    def test_get_return_not_set(self):
        result = self.execute("default-get")
        expected = "Default team not set. Default project not set."
        expect(result).to_be_like(expected)

    def test_get_return_team_only(self):
        self.execute("default-set", team=self.team)
        result = self.execute("default-get")
        expected = "Default team is '%s'. Default project not set." % self.team
        expect(result).to_be_like(expected)

    def test_get_return_project_only(self):
        self.execute("default-set", project=self.project)
        result = self.execute("default-get")
        expected = "Default team not set. Default project is '%s'." % self.project
        expect(result).to_be_like(expected)

    def test_get_return_team_and_project(self):
        self.execute("default-set", team=self.team, project=self.project)
        result = self.execute("default-get")
        expected = "Default team is '%s'. Default project is '%s'." % (self.team, self.project)
        expect(result).to_be_like(expected)
