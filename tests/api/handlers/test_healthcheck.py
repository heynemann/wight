#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from preggy import expect

from wight.api.config import Config
from tests.base import ApiTestCase


class HealthcheckHandlerTest(ApiTestCase):
    def test_healthcheck(self):
        response = self.fetch('/healthcheck')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_like('WORKING')


class HealthcheckWithCustomTextHandlerTest(ApiTestCase):
    def get_app(self):
        cfg = Config(HEALTHCHECK_TEXT="works")
        return self.create_api_app(cfg)

    def test_healthcheck(self):
        response = self.fetch('/healthcheck')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_like('works')
