#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import patch
from preggy import expect

from tests.factories import TeamFactory, LoadTestFactory
from tests.unit.base import WorkerTestCase
from wight.worker import BenchRunner, Repository


class TestBenchConfiguration(WorkerTestCase):

    @patch.object(Repository, 'clone')
    @patch.object(BenchRunner, '_save_last_commit')
    @patch.object(BenchRunner, 'validate_tests')
    @patch.object(BenchRunner, '_load_config_from_yml')
    @patch.object(BenchRunner, '_run_config_tests')
    def test_can_git_clone_in_specific_branch(self, run_config_mock, load_config_mock, validate_mock, save_mock, clone_mock):
        team = TeamFactory.create()
        TeamFactory.add_projects(team, 1)
        user = team.owner
        project = team.projects[0]
        load_test = LoadTestFactory.add_to_project(1, user=user, team=team, project=project, branch="test")

        runner = BenchRunner()
        runner.run_project_tests("some-path-doesnt-matter", str(load_test.uuid), duration=1)
        expect(clone_mock.call_args_list[0][1]['branch']).to_be_like(
            "test"
        )


