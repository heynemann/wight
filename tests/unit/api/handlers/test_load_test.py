#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import LoadTest
from tests.unit.base import FullTestCase
from tests.factories import TeamFactory, UserFactory


class ScheduleLoadTestTest(FullTestCase):
    def setUp(self):
        super(ScheduleLoadTestTest, self).setUp()

        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        self.project = self.team.add_project("schedule-test-project-1", "repo", self.user)

    def test_schedule_test(self):
        url = "/teams/%s/projects/%s/load_tests/" % (self.team.name, self.project.name)
        response = self.post(url)
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        tests = list(LoadTest.get_by_team_and_project_name(self.team, self.project.name))
        expect(tests).not_to_be_null()
        expect(tests).to_length(1)
        expect(tests[0].created_by.id).to_equal(self.user.id)
        expect(tests[0].project_name).to_equal(self.project.name)

    def test_schedule_test_without_being_a_member(self):
        team = TeamFactory.create()
        prj = team.add_project("bla", "repo", team.owner)

        url = "/teams/%s/projects/%s/load_tests/" % (team.name, prj.name)
        response = self.post(url)
        expect(response.code).to_equal(403)

    def test_schedule_test_for_invalid_project(self):
        url = "/teams/%s/projects/bogus-project/load_tests/" % self.team.name
        response = self.post(url)
        expect(response.code).to_equal(404)

    def test_schedule_test_for_invalid_team(self):
        url = "/teams/bogus-team/projects/bogus-project/load_tests/"
        response = self.post(url)
        expect(response.code).to_equal(404)
