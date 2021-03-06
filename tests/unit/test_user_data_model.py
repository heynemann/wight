#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tempfile
from unittest import TestCase
import os
from os.path import join, exists
from json import loads

from preggy import expect

from wight.models import UserData


class TestUserData(TestCase):
    def test_user_data_target(self):
        ud = UserData(target="http://target.wight.com")

        expect(ud.target).to_equal("http://target.wight.com")

    def test_user_data_serializes_properly(self):
        ud = UserData(target="http://target2.wight.com")

        directory = tempfile.mkdtemp()
        path = join(directory, '.wight-user-data')

        ud.save(path)

        with open(path, 'r') as text:
            obj = loads(text.read())
            expect(obj).to_include("target")
            expect(obj['target']).to_equal("http://target2.wight.com")

    def test_user_data_deserializes_properly(self):
        ud = UserData(target="http://target2.wight.com")

        directory = tempfile.mkdtemp()
        path = join(directory, '.wight-user-data')

        ud.save(path)

        loaded = UserData.load(path)
        expect(loaded.target).to_equal("http://target2.wight.com")

    def test_user_data_returns_none_from_invalid_path(self):
        loaded = UserData.load("/some/invalid/path")
        expect(loaded).to_be_null()

    def test_user_data_returns_from_default_path(self):
        if exists(UserData.DEFAULT_PATH):
            os.remove(UserData.DEFAULT_PATH)

        ud = UserData(target="http://target3.wight.com")
        ud.save()

        loaded = UserData.load()
        expect(loaded).not_to_be_null()
        expect(loaded.target).to_equal("http://target3.wight.com")

    def test_adding_team_default(self):
        ud = UserData(target="target")

        ud.set_default(team="team-blah")
        expect(hasattr(ud, "team")).to_be_true()
        expect(ud.team).to_equal("team-blah")
        expect(hasattr(ud, "project")).to_be_false()

    def test_adding_project_default(self):
        ud = UserData(target="target")

        ud.set_default(project="project-blah")
        expect(hasattr(ud, "project")).to_be_true()
        expect(ud.project).to_equal("project-blah")
        expect(hasattr(ud, "team")).to_be_false()

    def test_adding_team_and_project_default(self):
        ud = UserData(target="target")

        ud.set_default(team="team-blah", project="project-blah")
        expect(hasattr(ud, "team")).to_be_true()
        expect(hasattr(ud, "project")).to_be_true()
        expect(ud.team).to_equal("team-blah")
        expect(ud.project).to_equal("project-blah")

    def test_to_dict_with_team(self):
        ud = UserData(target="target")
        ud.set_default(team="team-blah")
        ud_dict = ud.to_dict()
        expect(ud_dict).to_be_like({"target": "target", "team": "team-blah", "token": None})

    def test_to_dict_with_project(self):
        ud = UserData(target="target")
        ud.set_default(project="project-blah")
        ud_dict = ud.to_dict()
        expect(ud_dict).to_be_like({"target": "target", "project": "project-blah", "token": None})

    def test_to_dict_with_team_and_project(self):
        ud = UserData(target="target")
        ud.set_default(team="team-blah", project="project-blah")
        ud_dict = ud.to_dict()
        expect(ud_dict).to_be_like({"target": "target", "team": "team-blah", "project": "project-blah", "token": None})

    def test_saving_with_team(self):
        ud = UserData(target="target")
        ud.set_default(team="team-blah")
        ud.save()
        loaded = UserData.load()
        expect(hasattr(loaded, "team")).to_be_true()
        expect(loaded.team).to_equal("team-blah")
        expect(hasattr(loaded, "project")).to_be_false()

    def test_saving_with_project(self):
        ud = UserData(target="target")
        ud.set_default(project="project-blah")
        ud.save()
        loaded = UserData.load()
        expect(hasattr(loaded, "project")).to_be_true()
        expect(loaded.project).to_equal("project-blah")
        expect(hasattr(loaded, "team")).to_be_false()
