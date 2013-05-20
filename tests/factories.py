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

from wight.models import User, Team, Project, LoadTest, TestConfiguration, TestResult, TestCycle, TestCycleTests, TestCyclePages, TestCycleRequests


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


class TestConfigurationFactory(factory.Factory):
    FACTORY_FOR = TestConfiguration

    title = factory.LazyAttributeSequence(lambda user, index: 'test-config-%d' % index)
    description = factory.LazyAttributeSequence(lambda user, index: 'test-config-desc-%d' % index)

    module = factory.LazyAttributeSequence(lambda user, index: 'module-test-%d' % index)
    class_name = factory.LazyAttributeSequence(lambda user, index: 'ModuleTest%d' % index)
    test_name = factory.LazyAttributeSequence(lambda user, index: 'test-config-name-%d' % index)
    target_server = factory.LazyAttributeSequence(lambda user, index: 'target-%d' % index)
    cycles = "[10,20,50,100]"
    cycle_duration = 30
    test_date = factory.LazyAttribute(lambda user: datetime.now())
    funkload_version = "1.0.0"

    sleep_time = 2
    sleep_time_min = 1
    sleep_time_max = 5

    startup_delay = 10
    apdex_default = 0.8


class TestCycleTestsFactory(factory.Factory):
    FACTORY_FOR = TestCycleTests

    successful_tests = factory.LazyAttributeSequence(lambda cycle, i: 10 * i)
    failed_tests = factory.LazyAttributeSequence(lambda cycle, i: i + 1)
    total_tests = factory.LazyAttribute(lambda cycle: cycle.successful_tests + cycle.failed_tests)
    failed_tests_percentage = factory.LazyAttribute(lambda c: c.failed_tests * 100 / c.total_tests )
    successful_tests_per_second = factory.LazyAttributeSequence(lambda cycle, i: 2 * i)


class TestCyclePagesFactory(factory.Factory):
    FACTORY_FOR = TestCyclePages
    apdex = .7

    total_pages = factory.LazyAttributeSequence(lambda cycle, i: 100 * i)
    successful_pages_per_second = factory.LazyAttributeSequence(lambda cycle, i: i)

    maximum_successful_pages_per_second = factory.LazyAttributeSequence(lambda cycle, i: 2 * i)

    successful_pages = factory.LazyAttributeSequence(lambda cycle, i: cycle.total_pages / 7)
    failed_pages = factory.LazyAttributeSequence(lambda cycle, i: cycle.total_pages - cycle.successful_pages)

    minimum = .2
    average = .5
    maximum = .8
    p10 = .9
    p50 = .8
    p90 = .4
    p95 = .3


class TestCycleRequestsFactory(factory.Factory):
    FACTORY_FOR = TestCycleRequests

    apdex = .7

    successful_requests_per_second = factory.LazyAttributeSequence(lambda cycle, i: 2 * i)
    maximum_successful_requests_per_second = factory.LazyAttributeSequence(lambda cycle, i: 2 * i)
    successful_requests = factory.LazyAttributeSequence(lambda cycle, i: 100 * i)
    failed_requests = factory.LazyAttributeSequence(lambda cycle, i: 10 * i)
    total_requests = factory.LazyAttribute(lambda c: c.successful_requests + c.failed_requests)

    minimum = .2
    average = .5
    maximum = .8
    p10 = .9
    p50 = .8
    p90 = .4
    p95 = .3


class TestCycleFactory(factory.Factory):
    FACTORY_FOR = TestCycle

    cycle_number = factory.LazyAttributeSequence(lambda cycle, i: 10 * i)
    concurrent_users = factory.LazyAttributeSequence(lambda cycle, i: 5 * i)

    test = factory.SubFactory(TestCycleTestsFactory)
    page = factory.SubFactory(TestCyclePagesFactory)
    request = factory.SubFactory(TestCycleRequestsFactory)


class TestResultFactory(factory.Factory):
    FACTORY_FOR = TestResult

    tests_executed = 100
    pages_visited = factory.LazyAttributeSequence(lambda result, i: result.tests_executed * i)
    requests_made = factory.LazyAttributeSequence(lambda result, i: result.tests_executed * i + 1)
    config = factory.SubFactory(TestConfigurationFactory)
    cycles = []

    @classmethod
    def _prepare(cls, create, **kwargs):
        test_result = super(TestResultFactory, cls)._prepare(create, **kwargs)
        test_result.cycles.append(TestCycleFactory.build())
        return test_result


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
    results = []

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

    @classmethod
    def add_test_result(cls, load_test, test_results=1):
        test_result = None
        for i in range(test_results):
            config = TestConfigurationFactory.create()
            test_result = TestResultFactory.create(config=config)
            load_test.results.append(test_result)
        return test_result


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

    @staticmethod
    def get_config():
        return {
            u'class': u'HealthCheckTest',
            u'class_description': u'Testando se o healthcheck aguenta carga.',
            u'class_title': u'HealthCheck Tests',
            u'configuration_file': u'/private/var/folders/th/z6vmj34j1gngpvwl5fg5t9440000gp/T/tmprkUn7b/HealthCheckTest.conf',
            u'cycle_time': u'1.0',
            u'cycles': u'[10, 20]',
            u'description': u'Testando se o healthcheck aguenta carga.',
            u'duration': u'5',
            u'id': u'test_healthcheck',
            u'log_xml': u'/private/var/folders/th/z6vmj34j1gngpvwl5fg5t9440000gp/T/tmprkUn7b/funkload.xml',
            u'method': u'test_healthcheck',
            u'module': u'test_healthcheck',
            u'node': u'HeynemannMBP',
            u'python_version': u'2.7.3',
            u'server_url': u'http://localhost:2368',
            u'sleep_time': u'0.01',
            u'sleep_time_max': u'0.5',
            u'sleep_time_min': u'0.0',
            u'startup_delay': u'0.01',
            'time': u'2013-05-17T17:39:01.511075',
            'version': u'1.16.1'
        }
