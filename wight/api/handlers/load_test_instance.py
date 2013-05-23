import tornado.web

from wight.api.handlers.base import BaseHandler
from wight.models import LoadTest
from json import dumps
from mongoengine import DoesNotExist


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
            }

            for result in load_test.results:
                last_cycle = result.cycles[-1]
                partial_result = {}
                partial_result['uuid'] = str(result.uuid)
                partial_result['concurrent_users'] = last_cycle.concurrent_users
                partial_result['title'] = result.config.title
                partial_result['requests_per_second'] = last_cycle.request.successful_requests_per_second
                partial_result['failed_requests'] = last_cycle.request.failed_requests
                partial_result['p95'] = last_cycle.request.p95

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
            load_test = LoadTest.objects.get(uuid=test_uuid)

            self.set_status(200)
            self.write(load_test.to_dict())
        except DoesNotExist:
            self.set_status(404)
        finally:
            self.finish()
