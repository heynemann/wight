#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from datetime import datetime
from uuid import uuid4

import factory

from wight.models import User, Team, Project, LoadTest


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    email = factory.LazyAttributeSequence(lambda user, index: 'user-%06d@example.com' % index)
    password = "12345"
    salt = None
    token = None
    token_expiration = None
    date_modified = factory.LazyAttribute(lambda user: datetime.now())
    date_created = factory.LazyAttribute(lambda user: datetime.now())
    with_token = False

    @classmethod
    def _prepare(cls, create, **kwargs):
        with_token = kwargs.pop('with_token', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)

        if with_token:
            user.validate_token()

        if create:
            user.save()
        return user

    @classmethod
    def get_default_password(cls):
        return cls.attributes()['password']


class TeamFactory(factory.Factory):
    FACTORY_FOR = Team

    name = factory.LazyAttributeSequence(lambda user, index: 'team-%d' % index)
    owner = factory.SubFactory(UserFactory)
    members = []
    projects = []
    date_modified = factory.LazyAttribute(lambda user: datetime.now())
    date_created = factory.LazyAttribute(lambda user: datetime.now())

    @classmethod
    def _prepare(cls, create, **kwargs):
        team = super(TeamFactory, cls)._prepare(create, **kwargs)
        if create:
            team.save()
        return team

    @classmethod
    def add_members(cls, team, number_of_members, with_token=False):
        for i in range(number_of_members):
            team.members.append(UserFactory.create(with_token=with_token))

        team.save()

    @classmethod
    def add_projects(cls, team, number_of_projects):
        for i in range(number_of_projects):
            team.projects.append(ProjectFactory.create(team=team, created_by=team.owner))

        team.save()


class ProjectFactory(factory.Factory):
    FACTORY_FOR = Project

    name = factory.LazyAttributeSequence(lambda user, index: 'project-%d' % index)
    repository = "git://github.com/heynemann/wight.git"
    created_by = factory.SubFactory(UserFactory)
    date_modified = factory.LazyAttribute(lambda user: datetime.now())
    date_created = factory.LazyAttribute(lambda user: datetime.now())
    team = factory.SubFactory(UserFactory)
    tests = []


class LoadTestFactory(factory.Factory):
    FACTORY_FOR = LoadTest

    uuid = factory.LazyAttribute(lambda user: uuid4())
    created_by = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)
    project_name = factory.LazyAttributeSequence(lambda user, index: 'project-%d' % index)
    base_url = factory.LazyAttributeSequence(lambda user, index: 'http://localhost:%04d' % index)
    status = "Scheduled"
    date_modified = factory.LazyAttribute(lambda user: datetime.now())
    date_created = factory.LazyAttribute(lambda user: datetime.now())

    @classmethod
    def _prepare(cls, create, **kwargs):
        load_test = super(LoadTestFactory, cls)._prepare(create, **kwargs)
        if create:
            load_test.save()
        return load_test

    @classmethod
    def add_to_project(cls, load_tests=1, user=None, team=None, project=None):
        if not user:
            user = UserFactory.create()

        if not team:
            team = TeamFactory.create(owner=user)

        if not project:
            TeamFactory.add_projects(team, 1)
            project = team.projects[-1]

        test = None
        for i in range(load_tests):
            test = LoadTestFactory.create(created_by=team.owner, team=team, project_name=project.name)

        return test


class FunkLoadTestResultPercentiles(object):
    def __init__(self, cycle, number_of_percentiles):
        self.name = "%03s" % cycle
        self.stepsize = 5
        self.results = []
        for i in xrange(0, 100, 5):
            value = (1 - i / 100)
            setattr(self, "perc%02s" % i, value)
            self.results.append(value)

    def calcPercentiles(self):
        pass


class FunkLoadTestResultPages(object):
    def __init__(self, cycle):
        self.finalized = False

        self.apdex = "0.993"
        self.apdex_score = "0.993"
        self.avg = "0.234"
        self.count = "200"
        self.cvus = cycle * 10 + 1
        self.cycle = "%03d" % cycle
        self.cycle_duration = "10"
        self.error = "0"
        self.error_percent = "0.0"
        self.max = "0.384"
        self.min = "0.123"
        self.per_second = {1368828264: 4, 1368828265: 33, 1368828266: 37, 1368828267: 32, 1368828268: 44, 1368828269: 26}
        self.rps = 35.2
        self.rps_max = 44.0
        self.rps_min = 0
        self.success = "300"
        self.tps = "20.30394"
        self.total = 0.99324

        self.percentiles = FunkLoadTestResultPercentiles(cycle, self.success)

    def finalize(self):
        self.finalized = True


class FunkLoadTestResultTests(object):
    def __init__(self, cycle):
        self.finalized = False

        self.avg = "0.234"
        self.count = "200"
        self.cvus = cycle * 10 + 1
        self.cycle = "%03d" % cycle
        self.cycle_duration = "10"
        self.error = "0"
        self.error_percent = "0.0"
        self.images = "2"
        self.links = "3"
        self.max = "0.384"
        self.min = "0.123"
        self.pages = "8"
        self.redirects = "12"
        self.success = "300"
        self.total = "0.99923"
        self.tps = "20.30394"
        self.traceback = []
        self.xmlrpc = "0"

        self.percentiles = FunkLoadTestResultPercentiles(cycle, self.success)

    def finalize(self):
        self.finalized = True


class FunkLoadTestResultFactory(object):
    @staticmethod
    def get_result(cycles):
        results = {}
        for cycle in xrange(cycles):
            cycle_key = "%03s" % cycle
            results[cycle_key] = {
                'test': FunkLoadTestResultTests(cycle),
                'response_step': None,
                'response': FunkLoadTestResultPages(cycle),
                'page': FunkLoadTestResultPages(cycle)
            }

        return results
