#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from json import dumps
from uuid import uuid4

from preggy import expect

from wight.models import LoadTest
from tests.unit.base import FullTestCase
from tests.factories import TeamFactory, UserFactory, LoadTestFactory, FunkLoadTestResultFactory


class SendLoadTestResultTest(FullTestCase):
    def setUp(self):
        super(SendLoadTestResultTest, self).setUp()

        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        self.project = self.team.add_project("send-load-result-test-project-1", "repo", self.user)

    def test_put_result(self):
        test = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project)

        config = FunkLoadTestResultFactory.get_config()
        cycles = FunkLoadTestResultFactory.get_result(4)

        result = dumps(LoadTest.get_data_from_funkload_results(config, cycles))

        url = "/teams/%s/projects/%s/load-tests/%s/result/" % (self.team.name, self.project.name, test.uuid)
        response = self.post(url, **{
            "result": result
        })
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        loaded_test = LoadTest.objects(uuid=test.uuid).first()
        expect(loaded_test).not_to_be_null()

        expect(loaded_test.results).to_length(1)
        expect(loaded_test.status).to_equal("Finished")

    def test_put_results_fails_when_result_not_found(self):
        test = LoadTestFactory.add_to_project(1, user=self.user, team=self.team, project=self.project)
        url = "/teams/%s/projects/%s/load-tests/%s/result/" % (self.team.name, self.project.name, test.uuid)
        response = self.post(url, **{
            "result": ""
        })
        expect(response.code).to_equal(400)

        response = self.post(url)
        expect(response.code).to_equal(400)

    def test_put_results_fails_when_invalid_test(self):
        config = FunkLoadTestResultFactory.get_config()
        cycles = FunkLoadTestResultFactory.get_result(4)

        result = dumps(LoadTest.get_data_from_funkload_results(config, cycles))

        url = "/teams/%s/projects/%s/load-tests/%s/result/" % (self.team.name, self.project.name, uuid4())
        response = self.post(url, **{
            "result": result
        })
        expect(response.code).to_equal(400)
