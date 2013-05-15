#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import tempfile
from os.path import exists, join

from preggy import expect

from wight.worker.repository import Repository
from tests.functional.base import TestCase


class TestCanCloneRepository(TestCase):
    def test_repository_is_created(self):
        temp_path = tempfile.mkdtemp()
        repo = Repository.clone("git://github.com/heynemann/wight.git", temp_path)
        repo.checkout('refs/heads/master')

        expect(repo.is_empty).to_be_false()
        expect(repo.is_bare).to_be_false()

        bench_path = join(temp_path, 'bench')
        expect(exists(bench_path)).to_be_true()

        conf_path = join(bench_path, 'wight.yml')
        expect(exists(conf_path)).to_be_true()
