#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from preggy import expect
from mock import patch

from wight.cli.base import WightDefaultController
from tests.base import TestCase


class TestDefaultHandler(TestCase):

    def test_meta_label(self):
        expect(WightDefaultController.Meta.label).to_equal('base')

    def test_meta_desc(self):
        expect(WightDefaultController.Meta.description).to_equal('wight load testing scheduler and tracker.')

    @patch('sys.stdout', new_callable=StringIO)
    def test_default_action(self, mock_stdout):
        expected = """
        usage: nosetests [-h] [--debug] [--quiet]

        optional arguments:
        -h, --help  show this help message and exit
        --debug     toggle debug output
        --quiet     suppress all output"""

        ctrl = self.make_controller(WightDefaultController)
        ctrl.default()

        expect(mock_stdout.getvalue()).to_be_like(expected)

    def test_load_conf(self):
#conf='/tmp/conf'
        ctrl = self.make_controller(WightDefaultController, conf=self.fixture_for('test.conf'))
        ctrl.load_conf()

        expect(ctrl.config).not_to_be_null()
