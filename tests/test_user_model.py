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
        user = User.create(email="user@gmail.com", password="12345")

        password = hmac.new(six.b(user.salt), six.b("12345"), hashlib.sha1).hexdigest()

        retrieved = User.objects(id=user.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().password).to_equal(password)
        expect(retrieved.first().email).to_equal("user@gmail.com")
        expect(retrieved.first().token).to_equal(user.token)

    def test_cant_create_user_with_same_email_twice(self):
        User.create(email="repeated@gmail.com", password="12345")
        user = User.create(email="repeated@gmail.com", password="12345")
        expect(user).to_be_null()

    def test_authenticating_with_wrong_pass_returns_none(self):
        user = User(email="user2@gmail.com", password="12345")
        user.save()

        expect(User.authenticate(email="user3@gmail.com", password="12345")).to_be_null()
        expect(User.authenticate(email="user2@gmail.com", password="54321")).to_be_null()

    def test_authenticating(self):
        user = User(email="user4@gmail.com", password="12345")
        user.save()

        auth_user = User.authenticate(email="user4@gmail.com", password="12345")
        expect(auth_user).not_to_be_null()

        expect(auth_user.token).not_to_be_null()
        expect(auth_user.token_expiration).not_to_be_null()

    def test_authenticate_using_invalid_token(self):
        auth_user = User.authenticate_with_token(token="12312412414124")
        expect(auth_user).to_be_null()

    def test_authenticate_using_expired_token(self):
        user = User(email="user6@gmail.com", password="12345")
        user.save()

        auth_user = User.authenticate(email="user6@gmail.com", password="12345", expiration=0)
        expect(auth_user).not_to_be_null()

        auth_user = User.authenticate_with_token(token=auth_user.token)
        expect(auth_user).to_be_null()

    def test_authenticate_using_token(self):
        user = User(email="user5@gmail.com", password="12345")
        user.save()

        auth_user = User.authenticate(email="user5@gmail.com", password="12345")
        expect(auth_user).not_to_be_null()

        auth_user = User.authenticate_with_token(token=auth_user.token)
        expect(auth_user).not_to_be_null()
