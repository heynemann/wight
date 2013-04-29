#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from json import dumps, loads


class UserData(object):
    def __init__(self, target):
        self.target = target

    def to_dict(self):
        return {
            "target": self.target
        }

    def write(self, path):
        with open(path, 'w') as serializable:
            serializable.write(dumps(self.to_dict()))

    @classmethod
    def from_dict(cls, data):
        item = cls(data['target'])
        return item

    @classmethod
    def load(cls, path):
        with open(path, 'r') as serializable:
            return cls.from_dict(loads(serializable.read()))
