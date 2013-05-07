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

from wight.models import Team, User
from tests.unit.base import FullTestCase


class TeamHandlerTest(FullTestCase):
    def setUp(self):
        super(TeamHandlerTest, self).setUp()

        email = "team-handler-test@gmail.com"
        self.user = User.objects.filter(email=email).first()

        if not self.user:
            self.user = User.create(email=email, password="12345")

    def test_create_team_without_auth(self):
        self.user = None
        response = self.post("/teams")
        expect(response.code).to_equal(401)

    def test_create_team(self):
        team_name = "test_team_creation"
        response = self.post("/teams", name=team_name)
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        team = Team.objects.filter(name=team_name).first()
        expect(team).not_to_be_null()

    def test_create_team_with_no_name_returns_bad_request(self):
        response = self.post("/teams")
        expect(response.code).to_equal(400)

    def test_duplicate_team(self):
        team_name = "test_team_creation_2"
        self.post("/teams", name=team_name)

        response = self.post("/teams", name=team_name)
        expect(response.code).to_equal(409)

    def test_get_team(self):
        Team.create(name="team3", owner=self.user)
        response = self.fetch_with_headers("/teams/team3")
        expect(response.code).to_equal(200)

        obj = response.body
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')

        expect(loads(obj)).to_be_like({
            "name": "team3",
            "owner": self.user.email,
            "members": []
        })

    def test_get_team_not_found(self):
        response = self.fetch_with_headers("/teams/team999999")
        expect(response.code).to_equal(404)

    def test_update_team(self):
        team = Team.create(name="team-4", owner=self.user)
        expect(team).not_to_be_null()

        response = self.put("/teams/team-4", name="new-name-4")
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        team = Team.objects.filter(name="new-name-4").first()
        expect(team).not_to_be_null()

    def test_update_team_to_empty_name(self):
        team = Team.create(name="team-empty", owner=self.user)
        expect(team).not_to_be_null()

        response = self.put("/teams/team-empty", name="")
        expect(response.code).to_equal(400)

        response = self.put("/teams/team-empty")
        expect(response.code).to_equal(400)

    def test_update_unknown_team(self):
        response = self.put("/teams/team9999999")
        expect(response.code).to_equal(404)

    def test_update_team_with_wrong_owner(self):
        u1 = User.create(email="team-wrong-owner-user", password="12345")
        expect(u1).not_to_be_null()
        team = Team.create(name="team-wrong-owner", owner=u1)
        expect(team).not_to_be_null()

        response = self.put("/teams/team-wrong-owner", name="new-name")
        expect(response.code).to_equal(403)
