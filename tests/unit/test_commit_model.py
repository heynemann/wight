#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from tempfile import mkdtemp
import datetime

from preggy import expect
from pygit2 import GIT_SORT_TIME

from wight.models import LoadTest, Commit
from wight.worker.repository import Repository
from tests.unit.base import ModelTestCase
from tests.factories import LoadTestFactory


class TestCommitModel(ModelTestCase):
    def test_can_create_commit(self):
        load_test = LoadTestFactory.create()

        retrieved = LoadTest.objects(id=load_test.id).first()
        commit = retrieved.last_commit
        expect(commit).not_to_be_null()
        expect(commit.hex).to_equal(load_test.last_commit.hex)

    def test_to_dict(self):
        load_test = LoadTestFactory.create()
        commit = load_test.last_commit
        json = commit.to_dict()

        expected_committer = {'name': u'Committer Name', 'email': u'Committer Name'}
        expected_author = {'name': u'Author Name', 'email': u'author@gmail.com'}

        expect(json['message']).to_equal(commit.commit_message)
        expect(json['hex']).to_equal('b64df0e7cdd3bcd099c4e43001f6c87efd81d417')
        expect(json['author']).to_be_like(expected_author)
        expect(json['committer']).to_be_like(expected_committer)

    def test_from_pygit(self):
        directory = mkdtemp()
        repo = Repository.clone(url="git://github.com/heynemann/wight.git", path=directory)
        head_commit = tuple(repo.walk(repo.head.target, GIT_SORT_TIME))[0]

        commit = Commit.from_pygit(head_commit)

        commit_date = datetime.datetime.fromtimestamp(head_commit.commit_time)

        expect(commit.hex).to_equal(head_commit.hex)

        expect(commit.author_name).to_equal(head_commit.author.name)
        expect(commit.author_email).to_equal(head_commit.author.email)

        expect(commit.committer_name).to_equal(head_commit.committer.name)
        expect(commit.committer_email).to_equal(head_commit.committer.email)

        expect(commit.commit_date).to_equal(commit_date)
