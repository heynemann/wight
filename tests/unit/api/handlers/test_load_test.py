#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from json import loads

from preggy import expect
import six

from wight.models import LoadTest
from tests.unit.base import FullTestCase
from tests.factories import TeamFactory, UserFactory, LoadTestFactory


class ScheduleLoadTestTest(FullTestCase):
    def setUp(self):
        super(ScheduleLoadTestTest, self).setUp()

        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        self.project = self.team.add_project("schedule-test-project-1", "repo", self.user)

    def test_schedule_test(self):
        url = "/teams/%s/projects/%s/load_tests/" % (self.team.name, self.project.name)
        response = self.post(url, **{
            "base_url": "http://www.globo.com"
        })
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        tests = list(LoadTest.get_by_team_and_project_name(self.team, self.project.name))
        expect(tests).not_to_be_null()
        expect(tests).to_length(1)
        expect(tests[0].created_by.id).to_equal(self.user.id)
        expect(tests[0].project_name).to_equal(self.project.name)
        expect(tests[0].base_url).to_equal("http://www.globo.com")
        expect(tests[0].simple).to_be_false()

    def test_schedule_a_test_in_a_specific_branch(self):
        url = "/teams/%s/projects/%s/load_tests/" % (self.team.name, self.project.name)
        response = self.post(url, **{
            "base_url": "http://www.globo.com",
            "branch": "test-branch"
        })
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        tests = list(LoadTest.get_by_team_and_project_name(self.team, self.project.name))
        expect(tests).not_to_be_null()
        expect(tests).to_length(1)
        expect(tests[0].base_url).to_equal("http://www.globo.com")
        expect(tests[0].git_branch).to_equal("test-branch")

    def test_simple_schedule_test(self):
        url = "/teams/%s/projects/%s/load_tests/" % (self.team.name, self.project.name)
        response = self.post(url, **{
            "base_url": "http://www.globo.com",
            "simple": "true",
        })
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        tests = list(LoadTest.get_by_team_and_project_name(self.team, self.project.name))
        expect(tests).not_to_be_null()
        expect(tests).to_length(1)
        expect(tests[0].created_by.id).to_equal(self.user.id)
        expect(tests[0].project_name).to_equal(self.project.name)
        expect(tests[0].base_url).to_equal("http://www.globo.com")
        expect(tests[0].simple).to_be_true()

    def test_schedule_test_without_being_a_member(self):
        team = TeamFactory.create()
        prj = team.add_project("bla", "repo", team.owner)

        url = "/teams/%s/projects/%s/load_tests/" % (team.name, prj.name)
        response = self.post(url, **{
            "base_url": "http://www.globo.com"
        })
        expect(response.code).to_equal(403)

    def test_schedule_test_for_invalid_project(self):
        url = "/teams/%s/projects/bogus-project/load_tests/" % self.team.name
        response = self.post(url, **{
            "base_url": "http://www.globo.com"
        })
        expect(response.code).to_equal(404)

    def test_schedule_test_for_invalid_team(self):
        url = "/teams/bogus-team/projects/bogus-project/load_tests/"
        response = self.post(url, **{
            "base_url": "http://www.globo.com"
        })
        expect(response.code).to_equal(404)

    def test_schedule_test_for_invalid_url(self):
        url = "/teams/%s/projects/%s/load_tests/" % (self.team.name, self.project.name)
        response = self.post(url, **{
            "base_url": ""
        })
        expect(response.code).to_equal(400)

        response = self.post(url)
        expect(response.code).to_equal(400)

        response = self.post(url, **{
            "base_url": "wqeqwejqwjeqw"
        })
        expect(response.code).to_equal(400)


class ListLoadTestsTest(FullTestCase):
    def setUp(self):
        super(ListLoadTestsTest, self).setUp()
        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        self.project = self.team.add_project("schedule-test-project-1", "repo", self.user)

    def test_get_return_401_if_not_authenticated(self):
        self.user = None
        url = "/teams/%s/projects/%s/load_tests/" % (self.team.name, self.project.name)
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(401)

    def test_get_return_400_if_quantity_not_passed(self):
        url = "/teams/%s/projects/%s/load_tests/" % (self.team.name, self.project.name)
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(400)

    def test_get_return_403_if_not_team_owner(self):
        user = UserFactory.create(with_token=True)
        team = TeamFactory.create(owner=user)
        project = team.add_project("schedule-test-project-1", "repo", user)
        url = "/teams/%s/projects/%s/load_tests/" % (team.name, project.name)
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(403)

    def test_get_return_200_if_not_team_owner_but_team_member(self):
        TeamFactory.add_members(self.team, 1, with_token=True)
        self.user = self.team.members[0]
        url = "/teams/%s/projects/%s/load_tests/?quantity=20" % (self.team.name, self.project.name)
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

    def test_get_load_tests_with_quantity(self):
        LoadTestFactory.add_to_project(24, user=self.user, team=self.team, project=self.project)
        url = "/teams/%s/projects/%s/load_tests/?quantity=16" % (self.team.name, self.project.name)
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

        obj = response.body
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')

        obj = loads(obj)
        expect(obj).to_length(16)
        load_test = LoadTest.objects(team=self.team, project_name=self.project.name).first()
        expect(obj[0]).to_be_like(load_test.to_dict())

    def test_get_load_tests_with_20_by_default_if_quantity_was_empty(self):
        LoadTestFactory.add_to_project(24, user=self.user, team=self.team, project=self.project)
        url = "/teams/%s/projects/%s/load_tests/?quantity=" % (self.team.name, self.project.name)
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

        obj = response.body
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')

        obj = loads(obj)
        expect(obj).to_length(20)
        load_test = LoadTest.objects(team=self.team, project_name=self.project.name).first()
        expect(obj[0]).to_be_like(load_test.to_dict())
