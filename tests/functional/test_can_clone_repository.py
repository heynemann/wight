#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tempfile

from preggy import expect

from wight.worker.repository import Repository
from tests.functional.base import TestCase


class TestCanCloneRepository(TestCase):
    def test_repository_is_bare(self):
        temp_path = tempfile.mkdtemp()
        repo = Repository.clone("git://github.com/heynemann/wight.git", temp_path)
        repo.checkout('refs/heads/master')

        expect(repo.is_empty).to_be_false()
        expect(repo.is_bare).to_be_false()
