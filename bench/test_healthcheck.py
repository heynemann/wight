#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import unittest

from funkload.FunkLoadTestCase import FunkLoadTestCase


class HealthCheckTest(FunkLoadTestCase):
    def setUp(self):
        self.server_url = '%s/healthcheck' % (self.conf_get('main', 'url').rstrip('/'),)

    def test_healthcheck(self):
        self.get(self.server_url, description='Get url')

if __name__ == '__main__':
    unittest.main()
