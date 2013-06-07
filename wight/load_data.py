#!/usr/bin/env python
# encoding: utf-8
import os
from os.path import join, dirname, abspath, expanduser, split
import sys
import argparse
from mongoengine import connect

from web.config import Config
from tests.factories import LoadTestFactory, TeamFactory, UserFactory, TestResultFactory, TestConfigurationFactory

print "Loading data..."

ROOT_PATH = abspath(join(dirname(__file__), '..'))
DEFAULT_CONFIG_PATH = join(ROOT_PATH, 'config', 'local.conf')


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', '-c', default=DEFAULT_CONFIG_PATH, help="Path to configuration file.")
    options = parser.parse_args(args)

    config = Config.load(path=options.conf, conf_name=split(options.conf)[-1], lookup_paths=[
        os.curdir,
        expanduser('~'),
        '/etc/',
    ])

    connect(
        config.MONGO_DB,
        host=config.MONGO_HOST,
        port=config.MONGO_PORT,
        username=config.MONGO_USER,
        password=config.MONGO_PASS
    )

    user = UserFactory.create()
    team = TeamFactory.create(owner=user)
    TeamFactory.add_projects(team, 1)
    project = team.projects[0]
    config = TestConfigurationFactory.build()
    load_test1 = LoadTestFactory.add_to_project(1, user=user, team=team, project=project)
    load_test1.results.append(TestResultFactory.build(config=config))
    load_test1.save()
    print "load test 1: %s" % load_test1.uuid
    print "test result for load test 1: %s" % load_test1.results[0].uuid
    load_test2 = LoadTestFactory.add_to_project(1, user=user, team=team, project=project)
    load_test2.results.append(TestResultFactory.build(config=config))
    load_test2.results.append(TestResultFactory.build())
    load_test2.save()
    print "load test 2: %s" % load_test2.uuid
    print "test result 1 for load test 2: %s" % load_test2.results[0].uuid
    print "test result 2 for load test 2: %s" % load_test2.results[1].uuid

if __name__ == '__main__':
    main(sys.argv[1:])
