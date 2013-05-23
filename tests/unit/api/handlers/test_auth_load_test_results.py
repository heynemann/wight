#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from json import loads
from uuid import uuid4

from preggy import expect
import six

from tests.unit.base import FullTestCase
from tests.factories import TeamFactory, UserFactory, LoadTestFactory, TestResultFactory


class ShowLoadTestResultTest(FullTestCase):
    def setUp(self):
        super(ShowLoadTestResultTest, self).setUp()
        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 1)
        self.project = self.team.projects[0]
        self.load_test = LoadTestFactory.create(created_by=self.user, team=self.team, project_name=self.project.name)
        self.load_test.results.append(TestResultFactory.build())
        self.load_test.save()
        self.result = self.load_test.results[0]

    def test_get_return_401_if_not_authenticated(self):
        self.user = None
        url = "/teams/%s/projects/%s/load-tests/%s/results/some-result-uuid" % (
            self.team.name, self.project.name, self.load_test.uuid
        )
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(401)

    def test_get_return_403_if_not_team_owner(self):
        user = UserFactory.create(with_token=True)
        team = TeamFactory.create(owner=user)
        url = "/teams/%s/projects/%s/load-tests/%s/results/some-result-uuid" % (
            team.name, self.project.name, self.load_test.uuid
        )
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(403)

    def test_get_should_return_200_if_no_errors(self):
        self.result = self.load_test.results[0]
        url = "/teams/%s/projects/%s/load-tests/%s/results/%s" % (
            self.team.name, self.project.name, self.load_test.uuid, self.result.uuid
        )
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

    def test_get_should_be_a_json(self):
        self.result = self.load_test.results[0]
        url = "/teams/%s/projects/%s/load-tests/%s/results/%s" % (
            self.team.name, self.project.name, self.load_test.uuid, self.result.uuid
        )
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)
        obj = response.body
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')
        try:
            loads(obj)
            assert True
        except ValueError:
            raise AssertionError("Should be possible to load a json from response")

    def test_get_should_be_a_equal_to_result_dict(self):
        url = "/teams/%s/projects/%s/load-tests/%s/results/%s" % (
            self.team.name, self.project.name, self.load_test.uuid, self.result.uuid
        )
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)
        obj = response.body
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')
        expect(loads(obj)).to_be_like(self.result.to_dict())

    def test_should_return_404_if_project_not_in_team(self):
        url = "/teams/%s/projects/whatever/load-tests/%s/results/whatever" % (
            self.team.name, self.load_test.uuid
        )
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(404)

    def test_should_return_404_if_load_test_not_in_project(self):
        url = "/teams/%s/projects/%s/load-tests/whatever/results/whatever" % (
            self.team.name, self.project.name
        )
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(404)

    def test_should_return_404_if_test_result_not_in_load_test(self):
        url = "/teams/%s/projects/%s/load-tests/%s/results/%s" % (
            self.team.name, self.project.name, self.load_test.uuid, uuid4()
        )
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(404)
