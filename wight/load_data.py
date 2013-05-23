#!/usr/bin/env python
# encoding: utf-8
import os
from os.path import join, dirname, abspath, expanduser, split
import sys
import argparse
from mongoengine import connect

from web.config import Config
from tests.factories import LoadTestFactory, TeamFactory, UserFactory, TestResultFactory

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
    load_test = LoadTestFactory.add_to_project(1, user=user, team=team, project=project)
    load_test.results.append(TestResultFactory.build())

    print "load test: %s" % load_test.uuid
    print "test result: %s" % load_test.results[0].uuid

if __name__ == '__main__':
    main(sys.argv[1:])
