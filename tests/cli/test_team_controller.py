#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from mock import patch

from wight.cli.team import CreateTeamController
from tests.base import TestCase


class TestCreateTeamController(TestCase):
    @patch.object(CreateTeamController, 'post')
    def test_create_team(self, post_mock):
        ctrl = self.make_controller(CreateTeamController, conf=self.fixture_for('test.conf'), team_name='nameless')
        ctrl.default()
        post_mock.assert_called_with("/teams", {"name": "nameless"})
