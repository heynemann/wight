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

from wight.models import Team
from tests.unit.base import FullTestCase
from tests.factories import UserFactory, TeamFactory


class TeamHandlerTest(FullTestCase):
    def setUp(self):
        super(TeamHandlerTest, self).setUp()

        self.user = UserFactory.create()

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
        team = TeamFactory.create(owner=self.user)
        response = self.fetch_with_headers("/teams/%s" % team.name)
        expect(response.code).to_equal(200)

        obj = response.body
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')

        expect(loads(obj)).to_be_like({
            "name": team.name,
            "owner": self.user.email,
            "members": []
        })

    def test_get_team_not_found(self):
        response = self.fetch_with_headers("/teams/team999999")
        expect(response.code).to_equal(404)

    def test_update_team(self):
        team = TeamFactory.create(owner=self.user)

        response = self.put("/teams/%s" % team.name, name="new-name-4")
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        team = Team.objects.filter(name=team.name).first()
        expect(team).not_to_be_null()

    def test_update_team_to_empty_name(self):
        team = TeamFactory.create(owner=self.user)

        response = self.put("/teams/%s" % team.name, name="")
        expect(response.code).to_equal(400)

        response = self.put("/teams/%s" % team.name)
        expect(response.code).to_equal(400)

    def test_update_unknown_team(self):
        response = self.put("/teams/team9999999")
        expect(response.code).to_equal(404)

    def test_update_team_with_wrong_owner(self):
        u1 = UserFactory.create()
        TeamFactory.create(owner=u1)

        response = self.put("/teams/team-wrong-owner", name="new-name")
        expect(response.code).to_equal(403)

    def test_add_user(self):
        user = UserFactory.create()
        team = TeamFactory.create(owner=self.user)
        expect(team).not_to_be_null()

        response = self.patch("/teams/%s/members" % team.name, user=user.email)
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        team = Team.objects.filter(name=team.name).first()
        expect(team).not_to_be_null()
        expect(team.members).to_include(user)

    def test_add_non_existent_user(self):
        team = TeamFactory.create(owner=self.user)
        expect(team).not_to_be_null()

        response = self.patch("/teams/%s/members" % team.name, user="Wrong@email.com")
        expect(response.code).to_equal(400)
        expect(response.body).to_equal("User not found")

    def test_add_to_non_existent_team(self):
        response = self.patch("/teams/team-10/members", user="Wrong@email.com")
        expect(response.code).to_equal(404)
        expect(response.body).to_equal("Team not found")

    def test_add_user_to_team_without_user(self):
        team = TeamFactory.create(owner=self.user)
        response = self.patch("/teams/%s/members" % team.name)
        expect(response.code).to_equal(400)
