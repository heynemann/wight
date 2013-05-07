#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import sys
from os.path import abspath, dirname, join
from unittest import TestCase as PythonTestCase

from mongoengine import connect
import sh

from wight.models import User, Team

ROOT_PATH = abspath(join(dirname(__file__), '../../wight/cli/__init__.py'))


class AcceptanceTest(PythonTestCase):
    @classmethod
    def setUpClass(cls):
        connect(
            "mongo-acceptance-test",
            host="localhost",
            port=7778
        )

        User.objects.delete()
        Team.objects.delete()

    def execute(self, command, *arguments, **kw):
        python = sh.Command(sys.executable)

        try:
            if 'stdin' in kw:
                stdin = kw['stdin']
                del kw['stdin']

                result = python(ROOT_PATH, command, _in=stdin, *arguments, **kw)
            else:
                result = python(ROOT_PATH, command, *arguments, **kw)
        except sh.ErrorReturnCode_1:
            error = sys.exc_info()[1]
            assert False, "Running %s returned status code 1. The error was: %s" % (command, error.stderr)

        result.wait()

        return result.strip()
