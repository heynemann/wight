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

    UUIDField, StringField, IntField, FloatField, DateTimeField, BooleanField, ListField,
    URLField, ReferenceField, EmbeddedDocumentField,  # fields

    DoesNotExist, Q)
from mongoengine.queryset import NotUniqueError


class UserData(object):
    DEFAULT_PATH = expanduser(environ.get('WIGHT_USERDATA_PATH', None) or "~/.wight")

    def __init__(self, target, token=None):
        self.target = target
        self.token = token

    def to_dict(self):
        return {
            "target": self.target,
            "token": self.token
        }

    def save(self, path=None):
        if path is None:
            path = UserData.DEFAULT_PATH

        with open(path, 'w') as serializable:
            serializable.write(dumps(self.to_dict()))

    @classmethod
    def from_dict(cls, data):
        item = cls(
            target=data['target'],
            token=data.get('token', None)
        )
        return item

    @classmethod
    def load(cls, path=None):
        if path is None:
            path = UserData.DEFAULT_PATH

        if not exists(path):
            return None

        with open(path, 'r') as serializable:
            return cls.from_dict(loads(serializable.read()))


def get_uuid():
    return str(uuid4())


class User(Document):
    email = StringField(max_length=2000, unique=True, required=True)
    password = StringField(max_length=2000, required=True)
    salt = UUIDField(required=False)
    token = StringField(required=False)
    token_expiration = DateTimeField(required=False)
    date_modified = DateTimeField(default=datetime.datetime.now)
    date_created = DateTimeField(default=datetime.datetime.now)

    def clean(self):
        if self.salt is None:
            self.salt = get_uuid()
            # Make sure that password is hashed
            self.password = User.get_hash_for(self.salt, self.password)

        # Updates date_modified field
        self.date_modified = datetime.datetime.now()

    def to_dict(self):
        return self.email

    def validate_token(self, expiration=2 * 60 * 24, generate=True):
        if generate:
            self.token = get_uuid()
        self.token_expiration = datetime.datetime.now() + datetime.timedelta(minutes=expiration)

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

        if user.token_expiration < datetime.datetime.now():
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
    date_modified = DateTimeField(default=datetime.datetime.now)
    date_created = DateTimeField(default=datetime.datetime.now)

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
        self.date_modified = datetime.datetime.now()

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
    date_modified = DateTimeField(default=datetime.datetime.now)
    date_created = DateTimeField(default=datetime.datetime.now)
    team = ReferenceField(Team, required=True)

    def clean(self):
        if self.created_by.id != self.team.owner.id:
            team_member_ids = [member.id for member in self.team.members]
            if self.created_by.id not in team_member_ids:
                raise ValueError("Only the owner or members of team %s can create projects for it." % self.team.name)

        # Updates date_modified field
        self.date_modified = datetime.datetime.now()

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


class TestCycleTests(EmbeddedDocument):
    successful_tests_per_second = FloatField(required=True)
    total_tests = IntField(required=True)
    successful_tests = IntField(required=True)
    failed_tests = IntField(required=True)
    failed_tests_percentage = FloatField(required=True)


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


class TestCycle(EmbeddedDocument):
    cycle_number = IntField(required=True)
    concurrent_users = IntField(required=True)

    test = EmbeddedDocumentField(TestCycleTests)
    page = EmbeddedDocumentField(TestCyclePages)
    request = EmbeddedDocumentField(TestCycleRequests)


class TestResult(EmbeddedDocument):
    uuid = UUIDField(required=True, default=uuid4())
    date_created = DateTimeField(default=datetime.datetime.now)
    date_modified = DateTimeField(default=datetime.datetime.now)

    tests_executed = IntField(required=True)
    pages_visited = IntField(required=True)
    requests_made = IntField(required=True)

    config = EmbeddedDocumentField(TestConfiguration)
    cycles = ListField(EmbeddedDocumentField(TestCycle))

    def clean(self):
        self.date_modified = datetime.datetime.now()


class LoadTest(Document):
    uuid = UUIDField(required=True, default=uuid4())
    status = StringField(required=True, choices=("Scheduled", "Running", "Finished"))
    team = ReferenceField(Team, required=True)
    created_by = ReferenceField(User, required=True)
    project_name = StringField(max_length=2000, required=True)
    base_url = URLField(max_length=2000, required=True)
    date_created = DateTimeField(default=datetime.datetime.now)
    date_modified = DateTimeField(default=datetime.datetime.now)

    results = ListField(EmbeddedDocumentField(TestResult))

    meta = {
        "ordering": ["-date_created"]
    }

    def clean(self):
        if self.created_by.id != self.team.owner.id:
            team_member_ids = [member.id for member in self.team.members]
            if self.created_by.id not in team_member_ids:
                raise ValueError("Only the owner or members of team %s can create tests for it." % self.team.name)

        self.date_modified = datetime.datetime.now()

    def to_dict(self):
        return {
            "uuid": str(self.uuid),
            "createdBy": self.created_by.email,
            "team": self.team.name,
            "project": self.project_name,
            "baseUrl": str(self.base_url),
            "status": self.status,
            "created": self.date_created.isoformat()[:19],
            "lastModified": self.date_modified.isoformat()[:19],
        }

    def add_result(self, config, stats):
        cfg = TestConfiguration(
            title=config['class_title'],
            description=config['class_description'],
            test_date=datetime.datetime.strptime(config['time'], "%Y-%m-%dT%H:%M:%S.%f"),
            funkload_version=config['version'],

            module=config['module'],
            class_name=config['class'],
            test_name=config['method'],

            target_server=config['server_url'],
            cycles=config['cycles'],
            cycle_duration=config['duration'],

            sleep_time=float(config['sleep_time']),
            sleep_time_min=float(config['sleep_time_min']),
            sleep_time_max=float(config['sleep_time_max']),

            startup_delay=float(config['startup_delay'])
        )

        for key, value in stats.items():
            value['test'].finalize()
            value['page'].finalize()
            value['response'].finalize()

            result = TestResult(
                tests_executed=value['test'].count,
                pages_visited=value['page'].count,
                requests_made=value['response'].count,
                config=cfg
            )

            self.results.append(result)

        self.save()

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
