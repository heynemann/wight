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
from tests.unit.base import ModelTestCase
from tests.factories import UserFactory


class TestUserModel(ModelTestCase):
    def test_can_create_user(self):
        user = UserFactory.create()

        password = UserFactory.get_default_password()
        password = hmac.new(six.b(str(user.salt)), six.b(password), hashlib.sha1).hexdigest()

        retrieved = User.objects(id=user.id)
        expect(retrieved.count()).to_equal(1)
        expect(retrieved.first().password).to_equal(password)
        expect(retrieved.first().email).to_equal(user.email)
        expect(retrieved.first().token).to_equal(user.token)

    def test_cant_create_user_with_same_email_twice(self):
        user = UserFactory.create()
        user = User.create(email=user.email, password="12345")
        expect(user).to_be_null()

    def test_authenticating_with_wrong_pass_returns_none(self):
        created_user = UserFactory.create()

        exists, user = User.authenticate(email="invalidemail@gmail.com", password="12345")
        expect(exists).to_be_false()
        expect(user).to_be_null()

        exists, user = User.authenticate(email=created_user.email, password="54312")
        expect(exists).to_be_true()
        expect(user).to_be_null()

    def test_authenticating(self):
        user = UserFactory.create()

        exists, auth_user = User.authenticate(email=user.email, password="12345")
        expect(exists).to_be_true()
        expect(auth_user).not_to_be_null()

        expect(auth_user.token).not_to_be_null()
        expect(auth_user.token_expiration).not_to_be_null()

    def test_authenticate_using_invalid_token(self):
        auth_user = User.authenticate_with_token(token="12312412414124")
        expect(auth_user).to_be_null()

    def test_authenticate_using_expired_token(self):
        user = UserFactory.create()

        exists, auth_user = User.authenticate(email=user.email, password=UserFactory.get_default_password(), expiration=0)
        expect(auth_user).not_to_be_null()

        auth_user = User.authenticate_with_token(token=auth_user.token)
        expect(auth_user).to_be_null()

    def test_authenticate_using_token(self):
        user = UserFactory.create()

        exists, auth_user = User.authenticate(email=user.email, password=UserFactory.get_default_password())
        expect(auth_user).not_to_be_null()

        auth_user = User.authenticate_with_token(token=auth_user.token)
        expect(auth_user).not_to_be_null()
