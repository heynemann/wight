#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import exists, expanduser
import datetime
from json import dumps, loads
import hashlib
import hmac
from uuid import uuid4

import six
from mongoengine import Document, StringField, DateTimeField


class UserData(object):
    DEFAULT_PATH = expanduser("~/.wight")

    def __init__(self, target):
        self.target = target

    def to_dict(self):
        return {
            "target": self.target
        }

    def write(self, path=None):
        if path is None:
            path = UserData.DEFAULT_PATH

        with open(path, 'w') as serializable:
            serializable.write(dumps(self.to_dict()))

    @classmethod
    def from_dict(cls, data):
        item = cls(data['target'])
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
    email = StringField(max_length=2000, required=True)
    password = StringField(max_length=2000, required=True)
    salt = StringField(required=True, default=get_uuid)
    token = StringField(required=False)
    token_expiration = DateTimeField(required=False)
    date_modified = DateTimeField(default=datetime.datetime.now)
    date_created = DateTimeField(default=datetime.datetime.now)

    def clean(self):
        # Make sure that password is hashed
        self.password = User.get_hash_for(self.salt, self.password)

        # Updates date_modified field
        self.date_modified = datetime.datetime.now()

    @classmethod
    def get_hash_for(cls, salt, password):
        return hmac.new(six.b(str(salt)), six.b(password), hashlib.sha1).hexdigest()

    @classmethod
    def authenticate(cls, email, password, expiration=2 * 60 * 24):
        user = User.objects.filter(email__iexact=email).first()

        if user is None:
            return None

        if user.password != cls.get_hash_for(user.salt, password):
            return None

        user.token = get_uuid()
        user.token_expiration = datetime.datetime.now() + datetime.timedelta(minutes=expiration)
        user.save()

        return user

    @classmethod
    def authenticate_with_token(cls, token, expiration=2 * 60 * 24):
        user = User.objects.filter(token=token).first()

        if user is None:
            return None

        if user.token_expiration < datetime.datetime.now():
            return None

        user.token_expiration = datetime.datetime.now() + datetime.timedelta(minutes=expiration)
        user.save()

        return user
