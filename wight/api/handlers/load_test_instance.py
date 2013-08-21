#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from uuid import UUID
from os.path import join

import tornado.web
from json import dumps
from mongoengine import DoesNotExist

from wight.models import LoadTest, Team
from wight.api.handlers.base import BaseHandler


class LoadTestInstanceHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, team_name=None, project_name=None, test_uuid=None):
        try:
            load_test = LoadTest.objects.get(uuid=test_uuid)

            response = {
                'uuid': str(load_test.uuid),
                'results': [],
                'status': load_test.status,
                'baseUrl': load_test.base_url,
                'teamName': load_test.team.name,
                'projectName': load_test.project_name,
                'createdBy': load_test.created_by.email,
                'created': load_test.date_created.isoformat()[:19],
                'lastModified': load_test.date_modified.isoformat()[:19],
                'repository': load_test.project.repository,
                'error': load_test.error,
                'lastCommit': load_test.last_commit and load_test.last_commit.to_dict() or None,
            }

            for result in load_test.results:
                cycles_sorted = sorted(result.cycles, key=lambda cycle: cycle.cycle_number)
                last_cycle = cycles_sorted[-1]
                partial_result = {
                    'uuid': str(result.uuid),
                    'concurrent_users': last_cycle.concurrent_users,
                    'title': result.config.title,
                    'requests_per_second': last_cycle.request.successful_requests_per_second,
                    'failed_requests': last_cycle.request.failed_requests,
                    'p95': last_cycle.request.p95
                }

                response['results'].append(partial_result)

            self.set_status(200)
            self.write(dumps(response))
        except DoesNotExist:
            self.set_status(404)
        finally:
            self.finish()


class LoadTestInstanceResultsHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, test_uuid=None):
        try:
            load_test = LoadTest.objects.get(uuid=UUID(test_uuid))
            self.set_status(200)
            self.write(load_test.to_dict())
        except DoesNotExist:
            try:
                load_test = LoadTest.objects.get(results__uuid=UUID(test_uuid))
                self.set_status(200)

                result = load_test.to_dict()
                result['reportURL'] = join(self.application.config.WIGHT_WEB_HOST.rstrip('/'), 'report', test_uuid)
                self.write(result)
            except DoesNotExist:
                self.set_status(404)
        finally:
            self.finish()


class LoadTestOrResultHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, uuid):
        self.set_status(200)
        try:
            load_test, test_result = LoadTest.get_test_result(uuid)
            return_value = {
                "team": load_test.team.name,
                "project": load_test.project_name,
                "result": test_result.to_dict(),
                "createdBy": load_test.created_by.email,
                "lastModified": load_test.date_modified.isoformat()[:19]
            }
            self.write(dumps(return_value))
        except DoesNotExist:
            load_test = LoadTest.objects(uuid=uuid)
            if not load_test.count():
                self.set_status(404)
                return
            self.write(dumps(load_test.first().to_dict()))
        finally:
            self.finish()


class LastResultForLoadTestHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, uuid):
        self.set_status(200)
        try:
            last_result = LoadTest.get_last_result_for(uuid)
            if last_result:
                self.write(dumps(last_result.to_dict()))
            else:
                self.set_status(404)
        except DoesNotExist:
            self.set_status(404)
        finally:
            self.finish()


class ResultsForTeamProjectAndTestHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, team_name, project_name, module, class_name, test_name):
        self.set_status(200)
        try:
            team = Team.objects(name=team_name).first()
            results = LoadTest.get_same_results_for_all_load_tests_from_project(team, project_name, module, class_name, test_name)
            response = []
            for result in results:
                response.append(result.to_dict())
            self.write(dumps(response))
        except DoesNotExist:
            self.set_status(404)
        finally:
            self.finish()
