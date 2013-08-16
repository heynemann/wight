#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os import environ
from os.path import exists, expanduser
import datetime
from json import dumps, loads
import hashlib
import hmac
from uuid import uuid4

import six
from mongoengine import (
    Document, EmbeddedDocument,  # documents

    UUIDField, StringField, IntField, FloatField, DateTimeField, ListField,
    URLField, ReferenceField, EmbeddedDocumentField,  # fields

    DoesNotExist, Q)
from mongoengine.queryset import NotUniqueError


def format_date_to_dict(date):
    return date.isoformat()[:19]


class UserData(object):
    DEFAULT_PATH = expanduser(environ.get('WIGHT_USERDATA_PATH', None) or "~/.wight")

    def __init__(self, target, token=None):
        self.target = target
        self.token = token

    def to_dict(self):
        user_data = {
            "target": self.target,
            "token": self.token,
        }

        if hasattr(self, "team"):
            user_data["team"] = self.team

        if hasattr(self, "project"):
            user_data["project"] = self.project

        return user_data

    def set_default(self, team=None, project=None):
        if team:
            self.team = team
        if project:
            self.project = project

    def save(self, path=None):
        if path is None:
            path = UserData.DEFAULT_PATH

        with open(path, 'w') as serializable:
            serializable.write(dumps(self.to_dict()))

    @classmethod
    def from_dict(cls, data):
        item = cls(
            target=data['target'],
            token=data.get('token', None),
        )
        if "team" in data:
            item.set_default(team=data["team"])
        if "project" in data:
            item.set_default(project=data["project"])
        return item

    @classmethod
    def load(cls, path=None):
        if path is None:
            path = UserData.DEFAULT_PATH

        if not exists(path):
            return None

        with open(path, 'r') as serializable:
            return cls.from_dict(loads(serializable.read()))


class User(Document):
    email = StringField(max_length=2000, unique=True, required=True)
    password = StringField(max_length=2000, required=True)
    salt = UUIDField(required=False)
    token = StringField(required=False)
    token_expiration = DateTimeField(required=False)
    date_modified = DateTimeField(default=datetime.datetime.utcnow)
    date_created = DateTimeField(default=datetime.datetime.utcnow)

    def clean(self):
        if self.salt is None:
            self.salt = uuid4()
            # Make sure that password is hashed
            self.password = User.get_hash_for(self.salt, self.password)

        # Updates date_modified field
        self.date_modified = datetime.datetime.utcnow()

    def to_dict(self):
        return self.email

    def validate_token(self, expiration=2 * 60 * 24, generate=True):
        if generate:
            self.token = str(uuid4())
        self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration)

    @classmethod
    def get_hash_for(cls, salt, password):
        return hmac.new(six.b(str(salt)), six.b(str(password)), hashlib.sha1).hexdigest()

    @classmethod
    def authenticate(cls, email, password, expiration=2 * 60 * 24):
        user = User.objects.filter(email__iexact=email).first()

        if user is None:
            return False, None

        if str(user.password) != cls.get_hash_for(user.salt, password):
            return True, None

        user.validate_token(expiration)
        user.save()

        return True, user

    @classmethod
    def authenticate_with_token(cls, token, expiration=2 * 60 * 24):
        user = User.objects.filter(token=token).first()

        if user is None:
            return None

        if user.token_expiration < datetime.datetime.utcnow():
            return None

        user.validate_token(expiration, generate=False)
        user.save()

        return user

    @classmethod
    def create(cls, email, password, expiration=2 * 60 * 24):
        user = User(email=email, password=password)
        user.validate_token(expiration=expiration)

        try:
            user.save()
        except NotUniqueError:
            return None

        return user


class Team(Document):
    name = StringField(max_length=2000, unique=True, required=True)
    owner = ReferenceField(User, required=True)
    members = ListField(ReferenceField(User))
    date_modified = DateTimeField(default=datetime.datetime.utcnow)
    date_created = DateTimeField(default=datetime.datetime.utcnow)

    projects = ListField(EmbeddedDocumentField("Project"))

    def clean(self):
        if self.owner in self.members:
            raise ValueError("Can't have a team owner in the members collection.")

        member_ids = [member.id for member in self.members]
        if len(member_ids) != len(set(member_ids)):
            raise ValueError("Can't have the same user twice in the members collection.")

        project_names = [project.name for project in self.projects]
        if len(project_names) != len(set(project_names)):
            raise ValueError("Can't have the same project twice in the projects collection.")

        # Updates date_modified field
        self.date_modified = datetime.datetime.utcnow()

    def to_dict(self):
        return {
            "name": self.name,
            "owner": self.owner.email,
            "members": [member.to_dict() for member in self.members],
            "projects": [project.to_dict() for project in self.projects]
        }

    @classmethod
    def create(cls, name, owner, members=None):
        team = Team(name=name, owner=owner, members=[])
        if members:
            for member in members:
                team.members.append(member)
        try:
            team.save()
        except NotUniqueError:
            return None

        return team

    def add_project(self, name, repository, created_by):
        prj = Project(name=name, created_by=created_by, repository=repository, team=self)
        self.projects.append(prj)
        self.save()

        return prj

    def update_project(self, project_name, new_name=None, new_repository=None):
        project_exists = False
        for project in self.projects:
            if project.name == project_name:
                project_exists = True
                project.name = new_name if new_name else project.name
                project.repository = new_repository if new_repository else project.repository
                break
        if project_exists:
            self.save()
        else:
            raise DoesNotExist("Project with name '%s' was not found." % project_name)

    def delete_project(self, project_name):
        self.projects = [project for project in self.projects if project.name != project_name]
        self.save()


class Project(EmbeddedDocument):
    name = StringField(max_length=2000, required=True)
    repository = StringField(max_length=3000, required=True)
    created_by = ReferenceField(User, required=True)
    date_modified = DateTimeField(default=datetime.datetime.utcnow)
    date_created = DateTimeField(default=datetime.datetime.utcnow)
    team = ReferenceField(Team, required=True)

    def clean(self):
        if self.created_by.id != self.team.owner.id:
            team_member_ids = [member.id for member in self.team.members]
            if self.created_by.id not in team_member_ids:
                raise ValueError("Only the owner or members of team %s can create projects for it." % self.team.name)

        # Updates date_modified field
        self.date_modified = datetime.datetime.utcnow()

    def to_dict(self):
        return {
            "name": self.name,
            "repository": self.repository,
            "createdBy": self.created_by.email
        }


class TestConfiguration(EmbeddedDocument):
    title = StringField(max_length=2000, required=True)
    description = StringField(max_length=2000, required=True)
    test_date = DateTimeField(required=True)
    funkload_version = StringField(max_length=255, required=True)

    module = StringField(required=True)
    class_name = StringField(required=True)
    test_name = StringField(required=True)
    target_server = StringField(required=True)
    cycles = StringField(required=True)
    cycle_duration = IntField(required=True)

    sleep_time = FloatField(required=True)
    sleep_time_min = FloatField(required=True)
    sleep_time_max = FloatField(required=True)

    startup_delay = FloatField(required=True)

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "testDate": format_date_to_dict(self.test_date),
            "funkloadVersion": self.funkload_version,
            "module": self.module,
            "className": self.class_name,
            "testName": self.test_name,
            "targetServer": self.target_server,
            "cycles": self.cycles,
            "cycleDuration": self.cycle_duration,
            "sleepTime": self.sleep_time,
            "sleepTimeMin": self.sleep_time_min,
            "sleepTimeMax": self.sleep_time_max,
            "startupDelay": self.startup_delay
        }


class TestCycleTests(EmbeddedDocument):
    successful_tests_per_second = FloatField(required=True)
    total_tests = IntField(required=True)
    successful_tests = IntField(required=True)
    failed_tests = IntField(required=True)
    failed_tests_percentage = FloatField(required=True)

    def to_dict(self):
        return {
            'successfulTestsPerSecond': self.successful_tests_per_second,
            'totalTests': self.total_tests,
            'successfulTests': self.successful_tests,
            'failedTests': self.failed_tests,
            'failedTestsPercentage': self.failed_tests_percentage
        }


class TestCyclePages(EmbeddedDocument):
    apdex = FloatField(required=True)
    successful_pages_per_second = FloatField(required=True)
    maximum_successful_pages_per_second = FloatField(required=True)

    total_pages = IntField(required=True)
    successful_pages = IntField(required=True)
    failed_pages = IntField(required=True)

    minimum = FloatField(required=True)
    average = FloatField(required=True)
    maximum = FloatField(required=True)
    p10 = FloatField(required=True)
    p50 = FloatField(required=True)
    p90 = FloatField(required=True)
    p95 = FloatField(required=True)

    def to_dict(self):
        return {
            "apdex": self.apdex,
            "successfulPagesPerSecond": self.successful_pages_per_second,
            "maxSuccessfulPagesPerSecond": self.maximum_successful_pages_per_second,
            "totalRequests": self.total_pages,
            "successfulRequests": self.successful_pages,
            "failedRequests": self.failed_pages,
            "failedRequestPercentage": (float(self.failed_pages) / self.total_pages) * 100,
            "minimum": self.minimum,
            "average": self.average,
            "maximum": self.maximum,
            "p10": self.p10,
            "p50": self.p50,
            "p90": self.p90,
            "p95": self.p95
        }


class TestCycleRequests(EmbeddedDocument):
    apdex = FloatField(required=True)
    successful_requests_per_second = FloatField(required=True)
    maximum_successful_requests_per_second = FloatField(required=True)
    total_requests = IntField(required=True)
    successful_requests = IntField(required=True)
    failed_requests = IntField(required=True)

    minimum = FloatField(required=True)
    average = FloatField(required=True)
    maximum = FloatField(required=True)
    p10 = FloatField(required=True)
    p50 = FloatField(required=True)
    p90 = FloatField(required=True)
    p95 = FloatField(required=True)

    def to_dict(self):
        return {
            "apdex": self.apdex,
            "successfulRequestsPerSecond": self.successful_requests_per_second,
            "maxSuccessfulRequestsPerSecond": self.maximum_successful_requests_per_second,
            "totalRequests": self.total_requests,
            "successfulRequests": self.successful_requests,
            "failedRequests": self.failed_requests,
            "failedRequestPercentage": (float(self.failed_requests) / self.total_requests) * 100,
            "minimum": self.minimum,
            "average": self.average,
            "maximum": self.maximum,
            "p10": self.p10,
            "p50": self.p50,
            "p90": self.p90,
            "p95": self.p95
        }


class TestCycle(EmbeddedDocument):
    cycle_number = IntField(required=True)
    concurrent_users = IntField(required=True)

    test = EmbeddedDocumentField(TestCycleTests)
    page = EmbeddedDocumentField(TestCyclePages)
    request = EmbeddedDocumentField(TestCycleRequests)

    def to_dict(self):
        return {
            "cycleNumber": self.cycle_number,
            "concurrentUsers": self.concurrent_users,
            "test": self.test.to_dict(),
            "page": self.page.to_dict(),
            "request": self.request.to_dict()
        }


class TestResult(EmbeddedDocument):
    uuid = UUIDField(required=True, default=uuid4)
    date_created = DateTimeField(default=datetime.datetime.utcnow)
    date_modified = DateTimeField(default=datetime.datetime.utcnow)

    tests_executed = IntField(required=True)
    pages_visited = IntField(required=True)
    requests_made = IntField(required=True)

    log = StringField(required=True)
    status = StringField(required=True, choices=("Failed", "Successful"))

    config = EmbeddedDocumentField(TestConfiguration)
    cycles = ListField(EmbeddedDocumentField(TestCycle))

    def to_dict(self):
        cycles_sorted = sorted(self.cycles, key=lambda cycle: cycle.cycle_number)
        return {
            "uuid": str(self.uuid),
            "testExecuted": self.tests_executed,
            "pageVisited": self.pages_visited,
            "requestMade": self.requests_made,
            "created": format_date_to_dict(self.date_created),
            "lastModified": format_date_to_dict(self.date_modified),
            "config": self.config.to_dict(),
            "cycles": [cycle.to_dict() for cycle in cycles_sorted]
        }

    def clean(self):
        self.date_modified = datetime.datetime.utcnow()


class Commit(EmbeddedDocument):
    '''Describes the last commit in the repository being used in a load test.'''
    hex = StringField(max_length=255, required=True)
    author_name = StringField(max_length=2000, required=True)
    author_email = StringField(max_length=2000, required=True)
    committer_name = StringField(max_length=2000, required=True)
    committer_email = StringField(max_length=2000, required=True)

    commit_message = StringField(max_length=2000, required=True)
    commit_date = DateTimeField(required=True)

    date_modified = DateTimeField(default=datetime.datetime.utcnow)
    date_created = DateTimeField(default=datetime.datetime.utcnow)

    def clean(self):
        # Updates date_modified field
        self.date_modified = datetime.datetime.utcnow()

    @classmethod
    def from_pygit(cls, commit_obj):
        commit_date = datetime.datetime.fromtimestamp(commit_obj.commit_time)

        return Commit(
            hex=commit_obj.hex,
            author_name=commit_obj.author.name,
            author_email=commit_obj.author.email,
            committer_name=commit_obj.committer.name,
            committer_email=commit_obj.committer.email,
            commit_message=commit_obj.message,
            commit_date=commit_date
        )

    def to_dict(self):
        return {
            'hex': self.hex,
            'author': {
                'name': self.author_name,
                'email': self.author_email
            },
            'committer': {
                'name': self.committer_name,
                'email': self.committer_name
            },
            'message': self.commit_message,
            'date': self.commit_date.isoformat()[:19]
        }


class LoadTest(Document):
    uuid = UUIDField(required=True, default=uuid4)
    status = StringField(required=True, choices=("Scheduled", "Running", "Failed", "Finished"))
    team = ReferenceField(Team, required=True)
    created_by = ReferenceField(User, required=True)
    last_commit = EmbeddedDocumentField(Commit)
    project_name = StringField(max_length=2000, required=True)
    base_url = URLField(max_length=2000, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow)
    date_modified = DateTimeField(default=datetime.datetime.utcnow)
    error = StringField(required=False)

    results = ListField(EmbeddedDocumentField(TestResult))

    meta = {
        "ordering": ["-date_created"]
    }

    def clean(self):
        if self.created_by.id != self.team.owner.id:
            team_member_ids = [member.id for member in self.team.members]
            if self.created_by.id not in team_member_ids:
                raise ValueError("Only the owner or members of team %s can create tests for it." % self.team.name)

        self.date_modified = datetime.datetime.utcnow()

    @property
    def project(self):
        prj = [project for project in self.team.projects if project.name.lower() == self.project_name.lower()]

        return prj and prj[0] or None

    def to_dict(self):
        return {
            "uuid": str(self.uuid),
            "createdBy": self.created_by.email,
            "team": self.team.name,
            "project": self.project_name,
            "baseUrl": str(self.base_url),
            "status": self.status,
            "created": format_date_to_dict(self.date_created),
            "lastModified": format_date_to_dict(self.date_modified),
            "lastCommit": self.last_commit and self.last_commit.to_dict() or None,
            "results": [result.to_dict() for result in self.results]
        }

    def add_result(self, result, log):
        config, stats = result['config'], result['results']

        cfg = TestConfiguration(
            title=config['title'],
            description=config['description'],
            test_date=datetime.datetime.strptime(config['test_date'], "%Y-%m-%dT%H:%M:%S.%f"),
            funkload_version=config['funkload_version'],

            module=config['module'],
            class_name=config['class_name'],
            test_name=config['test_name'],

            target_server=config['target_server'],
            cycles=config['cycles'],
            cycle_duration=config['cycle_duration'],

            sleep_time=config['sleep_time'],
            sleep_time_min=config['sleep_time_min'],
            sleep_time_max=config['sleep_time_max'],

            startup_delay=config['startup_delay']
        )

        result = TestResult(
            tests_executed=stats['tests_executed'],
            pages_visited=stats['tests_executed'],
            requests_made=stats['requests_made'],
            config=cfg,
            log=log,
            status="Successful"
        )

        self.results.append(result)

        for value in stats['cycles']:
            cycle = TestCycle(
                cycle_number=value['cycle_number'],
                concurrent_users=value['concurrent_users']
            )

            test = value['test']
            cycle.test = TestCycleTests(
                successful_tests_per_second=test['successful_tests_per_second'],
                total_tests=test['total_tests'],
                successful_tests=test['successful_tests'],
                failed_tests=test['failed_tests'],
                failed_tests_percentage=test['failed_tests_percentage']
            )

            page = value['page']

            cycle.page = TestCyclePages(
                apdex=page['apdex'],
                successful_pages_per_second=page['successful_pages_per_second'],
                maximum_successful_pages_per_second=page['maximum_successful_pages_per_second'],

                total_pages=page['total_pages'],
                successful_pages=page['successful_pages'],
                failed_pages=page['failed_pages'],

                minimum=page['minimum'],
                average=page['average'],
                maximum=page['maximum'],
                p10=page['p10'],
                p50=page['p50'],
                p90=page['p90'],
                p95=page['p95']
            )

            request = value['request']

            cycle.request = TestCycleRequests(
                apdex=request['apdex'],
                successful_requests_per_second=request['successful_requests_per_second'],
                maximum_successful_requests_per_second=request['maximum_successful_requests_per_second'],

                total_requests=request['total_requests'],
                successful_requests=request['successful_requests'],
                failed_requests=request['failed_requests'],

                minimum=request['minimum'],
                average=request['average'],
                maximum=request['maximum'],
                p10=request['p10'],
                p50=request['p50'],
                p90=request['p90'],
                p95=request['p95']
            )

            result.cycles.append(cycle)

        self.save()

    @classmethod
    def get_data_from_funkload_results(cls, config, cycles):
        return {
            'config': cls.parse_config(config),
            'results': cls.parse_cycles(cycles)
        }

    @classmethod
    def parse_config(cls, config):
        return {
            'title': config['class_title'],
            'description': config['class_description'],
            'test_date': config['time'],
            'funkload_version': config['version'],

            'module': config['module'],
            'class_name': config['class'],
            'test_name': config['method'],

            'target_server': config['server_url'],
            'cycles': config['cycles'],
            'cycle_duration': int(config['duration']),

            'sleep_time': float(config['sleep_time']),
            'sleep_time_min': float(config['sleep_time_min']),
            'sleep_time_max': float(config['sleep_time_max']),

            'startup_delay': float(config['startup_delay'])
        }

    @classmethod
    def parse_cycles(cls, cycles):
        result = {
            'tests_executed': 0,
            'pages_visited': 0,
            'requests_made': 0,
            'cycles': []
        }

        for key, value in cycles.items():
            value['test'].finalize()
            value['page'].finalize()
            value['response'].finalize()

            result['tests_executed'] += int(value['test'].count)
            result['pages_visited'] += int(value['page'].count)
            result['requests_made'] += int(value['response'].count)

            cycle = {
                'cycle_number': int(key),
                'concurrent_users': int(value['test'].cvus)
            }

            test = value['test']
            cycle['test'] = {
                'successful_tests_per_second': float(test.tps),
                'total_tests': int(test.count),
                'successful_tests': int(test.success),
                'failed_tests': int(test.error),
                'failed_tests_percentage': float(float(test.error) / float(test.count)) * 100
            }

            page = value['page']

            page.percentiles.calcPercentiles()

            cycle['page'] = {
                'apdex': float(page.apdex_score),
                'successful_pages_per_second': float(page.rps),
                'maximum_successful_pages_per_second': float(page.rps_max),

                'total_pages': int(page.count),
                'successful_pages': int(page.success),
                'failed_pages': int(page.error),

                'minimum': float(page.min),
                'average': float(page.avg),
                'maximum': float(page.max),
                'p10': float(page.percentiles.perc10),
                'p50': float(page.percentiles.perc50),
                'p90': float(page.percentiles.perc90),
                'p95': float(page.percentiles.perc95)
            }

            response = value['response']

            response.percentiles.calcPercentiles()

            cycle['request'] = {
                'apdex': float(response.apdex_score),
                'successful_requests_per_second': float(response.rps),
                'maximum_successful_requests_per_second': float(response.rps_max),

                'total_requests': int(response.count),
                'successful_requests': int(response.success),
                'failed_requests': int(response.error),

                'minimum': float(response.min),
                'average': float(response.avg),
                'maximum': float(response.max),
                'p10': float(response.percentiles.perc10),
                'p50': float(response.percentiles.perc50),
                'p90': float(response.percentiles.perc90),
                'p95': float(response.percentiles.perc95)
            }

            result['cycles'].append(cycle)

        return result

    @classmethod
    def get_by_team_and_project_name(cls, team, project_name):
        return cls.get_sliced_by_team_and_project_name(team, project_name, 20)

    @classmethod
    def get_by_team(cls, team, quantity=5):
        results = []
        for project in team.projects:
            results.extend(cls.get_sliced_by_team_and_project_name(team, project.name, quantity))
        return results

    @classmethod
    def get_sliced_by_team_and_project_name(cls, team, project_name, quantity):
        return LoadTest.objects(team=team, project_name=project_name)[:quantity]

    @classmethod
    def get_by_user(cls, user):
        results = []
        teams = Team.objects(Q(members__contains=user) | Q(owner=user))
        for team in teams:
            results.extend(cls.get_by_team(team, quantity=3))
        return results

    @classmethod
    def get_test_result(cls, test_result_uuid):
        load_test = LoadTest.objects(results__uuid=test_result_uuid)
        if not load_test.count():
            raise DoesNotExist("There is no Load Test with a Test Result with uuid '%s'" % test_result_uuid)
        load_test = load_test.first()
        for result in load_test.results:
            if str(result.uuid) == test_result_uuid:
                return load_test, result
        raise DoesNotExist("There is no Test Result with uuid '%s' in Load Test '%s'" % (test_result_uuid, load_test.uuid))

    @classmethod
    def result_was_for(cls, result, module, class_name, test_name):
        return (result.config.module == module and
                result.config.class_name == class_name and
                result.config.test_name == test_name)

    @classmethod
    def get_last_result_for(cls, test_result_uuid):
        load_test, test_result = cls.get_test_result(test_result_uuid)
        load_tests = LoadTest.objects(uuid__ne=load_test.uuid, project_name=load_test.project_name)

        for other_load_test in load_tests:
            for result in other_load_test.results:
                if cls.result_was_for(result, test_result.config.module, test_result.config.class_name, test_result.config.test_name):
                    return result

        return None

    @classmethod
    def get_same_results_for_all_load_tests_from_project(cls, team, project_name, module, class_name, test_name):
        load_tests = LoadTest.objects(
            team=team, project_name=project_name,
            results__config__module=module,
            results__config__class_name=class_name,
            results__config__test_name=test_name
        )
        if not load_tests.count():
            raise DoesNotExist("There is no Load Test for team %s, project %s and test %s.%s.%s " % (
                team.name, project_name, module, class_name, test_name)
            )
        results = []
        for load_test in load_tests:
            for result in load_test.results:
                if cls.result_was_for(result, module, class_name, test_name):
                    results.append(result)
        return results
