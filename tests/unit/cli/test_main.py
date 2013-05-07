#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from cement.core import backend

from mock import patch, call
from preggy import expect

from wight.cli import main
from tests.unit.base import TestCase



class TestMain(TestCase):
    @patch('wight.cli.WightApp')
    def test_main_instantiate_app(self, app_mock):
        main()
        defaults = backend.defaults('wight', 'log')
        defaults['log']['level'] = 'WARN'
        app_mock.assert_called_with(config_defaults=defaults)
        expect(app_mock.mock_calls).to_be_like(
            [
                call(config_defaults={'wight': {}, 'log': {'level': 'WARN'}}),
                call().register_controllers(),
                call().setup(),
                call().run(),
                call().close()
            ]
        )
