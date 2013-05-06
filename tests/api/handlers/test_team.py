#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import Team
from tests.base import ApiTestCase


class TeamHandlerTest(ApiTestCase):
    def test_create_team(self):
        team_name = "test_team_creation"
        response = self.post(self.reverse_url('team'), name=team_name)
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        team = Team.objects.filter(name=team_name).first()
        expect(team).not_to_be_null()

    def test_create_team_with_no_name_returns_bad_request(self):
        response = self.post(self.reverse_url('team'))
        expect(response.code).to_equal(400)

    def test_duplicate_team(self):
        team_name = "test_team_creation_2"
        self.post(self.reverse_url('team'), name=team_name)

        response = self.post(self.reverse_url('team'), name=team_name)
        expect(response.code).to_equal(403)
