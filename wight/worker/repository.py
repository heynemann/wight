#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com


from pygit2 import clone_repository


class Repository(object):
    @classmethod
    def clone(cls, url, path, branch='refs/heads/master'):
        repo = clone_repository(url, path, bare=False)
        repo.checkout(branch)
        return repo
