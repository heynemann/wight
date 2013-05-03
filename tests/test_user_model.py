#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import hmac
import hashlib

from preggy import expect
import six

from wight.models import User
from tests.base import ModelTestCase


class TestUserModel(ModelTestCase):
    def test_can_create_user(self):
        user = User(email="heynemann@gmail.com", password="12345")
        user.save()

        password = hmac.new(six.b(user.salt), six.b("12345"), hashlib.sha1).hexdigest()

        retrieved = User.objects(id=user.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().password).to_equal(password)
