#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.models import User
from tests.unit.base import ApiTestCase


class UserAuthenticationTest(ApiTestCase):
    def test_authenticate_with_valid_user(self):
        user = User(email="test_auth1@gmail.com", password="12345")
        user.save()

        response = self.fetch_with_headers(self.reverse_url('auth_user'), email="test_auth1@gmail.com", password="12345")
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        user = User.objects.filter(email="test_auth1@gmail.com").first()

        expect(response.headers).to_include('Token-Expiration')
        # without nano seconds
        expect(response.headers['Token-Expiration'][:19]).to_equal(user.token_expiration.isoformat()[:19])

        expect(response.headers).to_include('Token')
        expect(response.headers['Token']).to_equal(user.token)

    def test_authenticate_with_invalid_user_should_be_not_found(self):
        response = self.fetch_with_headers(self.reverse_url('auth_user'), email="test_auth99999@gmail.com", password="12345")
        expect(response.code).to_equal(404)

    def test_authenticate_with_invalid_pass_should_be_access_denied(self):
        user = User(email="test_auth2@gmail.com", password="12345")
        user.save()

        response = self.fetch_with_headers(self.reverse_url('auth_user'), email="test_auth2@gmail.com", password="12346")
        expect(response.code).to_equal(403)

    def test_authenticate_with_no_headers_should_be_bad_request(self):
        response = self.fetch('/auth/user/')
        expect(response.code).to_equal(400)


class UserAuthenticationWithTokenTest(ApiTestCase):
    def test_authenticate_with_valid_user(self):
        email = "test_auth_token1@gmail.com"
        password = "12345"
        user = User(email=email, password=password)
        user.save()

        exists, user = User.authenticate(email=email, password=password)

        response = self.fetch_with_headers(self.reverse_url('auth_token'), token=user.token)
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        user = User.objects.filter(email=email).first()

        expect(response.headers).to_include('Token-Expiration')
        # without nano seconds
        expect(response.headers['Token-Expiration'][:19]).to_equal(user.token_expiration.isoformat()[:19])

        expect(response.headers).to_include('Token')
        expect(response.headers['Token']).to_equal(user.token)

    def test_authenticate_with_invalid_token(self):
        response = self.fetch_with_headers(self.reverse_url('auth_token'), token="invalid-token")
        expect(response.code).to_equal(403)

    def test_authenticate_with_no_headers(self):
        response = self.fetch(self.reverse_url('auth_token'))
        expect(response.code).to_equal(400)


class UserRegisterTest(ApiTestCase):
    def test_registering_valid_user(self):
        email = "test_register_1@gmail.com"
        response = self.fetch_with_headers(self.reverse_url('register_user'), email=email, password="12345")
        expect(response.code).to_equal(200)
        expect(response.body).to_equal("OK")

        user = User.objects.filter(email=email).first()

        expect(response.headers).to_include('Token-Expiration')
        # without nano seconds
        expect(response.headers['Token-Expiration'][:19]).to_equal(user.token_expiration.isoformat()[:19])

        expect(response.headers).to_include('Token')
        expect(response.headers['Token']).to_equal(user.token)

    def test_registering_duplicated_user(self):
        email = "test_register_2@gmail.com"
        password = "12345"
        user = User(email=email, password=password)
        user.save()

        response = self.fetch_with_headers(self.reverse_url('register_user'), email=email, password=password)
        expect(response.code).to_equal(409)
        expect(response.body).to_equal("User already registered.")

    def test_authenticate_with_invalid_headers(self):
        response = self.fetch_with_headers(self.reverse_url('register_user'), email="", password="")
        expect(response.code).to_equal(400)

    def test_authenticate_with_no_headers(self):
        response = self.fetch(self.reverse_url('register_user'))
        expect(response.code).to_equal(400)
