import tornado.web

from wight.api.handlers.base import BaseHandler
from wight.models import LoadTest
from json import dumps
from mongoengine import DoesNotExist


class LoadTestInstanceHandler(BaseHandler):

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    @BaseHandler.team_member
    def get(self, team, project_name, test_uuid):
        try:
            load_test = LoadTest.objects.get(uuid=test_uuid)
            response = {'uuid': str(load_test.uuid), 'results': [], 'status': load_test.status}
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
