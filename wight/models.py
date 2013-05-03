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
    date_modified = DateTimeField(default=datetime.datetime.now)
    date_created = DateTimeField(default=datetime.datetime.now)

    def clean(self):
        # Make sure that password is hashed
        self.password = hmac.new(six.b(self.salt), six.b(self.password), hashlib.sha1).hexdigest()

        # Updates date_modified field
        self.date_modified = datetime.datetime.now()
