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
from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField
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
    salt = StringField(required=False)
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
        return (hmac.new(six.b(str(salt)), six.b(str(password)), hashlib.sha1).hexdigest())

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

    def clean(self):
        if self.owner in self.members:
            raise ValueError("Can't have a team owner in the members collection.")

        member_ids = [member.id for member in self.members]
        if len(member_ids) != len(set(member_ids)):
            raise ValueError("Can't have the same user twice in the members collection.")

        # Updates date_modified field
        self.date_modified = datetime.datetime.now()

    def to_dict(self):
        return {
            "name": self.name,
            "owner": self.owner.email,
            "members": [member.to_dict() for member in self.members]
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
