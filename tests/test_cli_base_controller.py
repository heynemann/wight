#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from StringIO import StringIO

from cement.utils import test
from preggy import expect
from mock import patch

from wight.cli.base import WightBaseController


class TestBaseHandler(test.CementTestCase):

    def test_meta_label(self):
        expect(WightBaseController.Meta.label).to_equal('base')

    def test_meta_desc(self):
        expect(WightBaseController.Meta.description).to_equal('wight load testing scheduler and tracker.')

    @patch('sys.stdout', new_callable=StringIO)
    def test_default_action(self, mock_stdout):
        expected = """
        usage: nosetests [-h] [--debug] [--quiet]

        optional arguments:
        -h, --help  show this help message and exit
        --debug     toggle debug output
        --quiet     suppress all output"""

        self.app.setup()

        ctrl = WightBaseController()
        ctrl.app = self.app
        ctrl.default()

        expect(mock_stdout.getvalue()).to_be_like(expected)
