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
from tests.factories import TeamFactory, UserFactory, LoadTestFactory, TestResultFactory, TestConfigurationFactory


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

    def test_get_return_200_if_not_authenticated(self):
        self.user = None
        url = "/load-test-result/%s" % self.load_test.uuid
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

    def test_get_return_200_if_not_team_owner(self):
        user = UserFactory.create(with_token=True)
        team = TeamFactory.create(owner=user)
        url = "/load-test-result/%s" % self.load_test.uuid
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

    def test_get_should_return_200_if_no_errors(self):
        url = "/load-test-result/%s" % self.load_test.uuid
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

    def test_get_should_be_a_json(self):
        url = "/load-test-result/%s" % self.load_test.uuid
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

    def test_should_get_404_if_no_test_result(self):
        url = "/load-test-result/%s" % uuid4()
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(404)


class ShowLoadLastTestResultTest(FullTestCase):
    def setUp(self):
        super(ShowLoadLastTestResultTest, self).setUp()
        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        TeamFactory.add_projects(self.team, 1)
        self.project = self.team.projects[0]
        self.load_test = LoadTestFactory.create(created_by=self.user, team=self.team, project_name=self.project.name)
        self.load_test.results.append(TestResultFactory.build())
        self.load_test.save()
        self.result = self.load_test.results[0]

    def _add_results_for_last(self):
        config = TestConfigurationFactory.build()
        self.load_test.results.append(TestResultFactory.build(config=config))
        self.load_test.results.append(TestResultFactory.build())
        self.load_test.save()
        self.load_test2 = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project)
        self.load_test2.results.append(TestResultFactory.build())
        self.load_test2.results.append(TestResultFactory.build(config=config))
        self.load_test2.save()

    def test_get_return_200_if_not_authenticated(self):
        self._add_results_for_last()
        self.user = None
        url = "/load-test-result/%s/last/" % self.load_test2.results[1].uuid
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

    def test_get_return_200_if_not_team_owner(self):
        self._add_results_for_last()
        user = UserFactory.create(with_token=True)
        TeamFactory.create(owner=user)
        url = "/load-test-result/%s/last/" % self.load_test2.results[1].uuid
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

    def test_get_should_return_200_if_no_errors(self):
        self._add_results_for_last()
        url = "/load-test-result/%s/last/" % self.load_test2.results[1].uuid
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

    def test_get_should_be_a_json(self):
        self._add_results_for_last()
        url = "/load-test-result/%s/last/" % self.load_test2.results[1].uuid
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

    def test_get_should_be_equal_last_result_to_dict(self):
        self._add_results_for_last()
        result1 = self.load_test.results[1]
        result2 = self.load_test2.results[1]

        url = "/load-test-result/%s/last/" % result2.uuid
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)
        result = loads(response.body)
        expect(result["uuid"]).to_equal(str(result1.uuid))

    def test_should_get_404_if_no_test_result(self):
        url = "/load-test-result/%s/last/" % uuid4()
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(404)

    def test_should_get_404_if_no_last_test_result(self):
        url = "/load-test-result/%s/last/" % self.result.uuid
        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(404)
