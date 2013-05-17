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
