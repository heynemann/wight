#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import Team
from tests.acceptance.base import AcceptanceTest


class TestTeam(AcceptanceTest):

    def test_can_create_team(self):
        team_name = "test-create-team"

        result = self.execute("create-team", team_name)
        expect(result).to_equal("Created 'test-create-team' team in '%s' target." % self.target)

        team = Team.objects.filter(name=team_name).first()
        expect(team).not_to_be_null()
