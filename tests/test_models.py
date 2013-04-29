#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tempfile
from unittest import TestCase
from os.path import join
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

        ud.write(path)

        with open(path, 'r') as text:
            obj = loads(text.read())
            expect(obj).to_include("target")
            expect(obj['target']).to_equal("http://target2.wight.com")

    def test_user_data_deserializes_properly(self):
        ud = UserData(target="http://target2.wight.com")

        directory = tempfile.mkdtemp()
        path = join(directory, '.wight-user-data')

        ud.write(path)

        loaded = UserData.load(path)
        expect(loaded.target).to_equal("http://target2.wight.com")
