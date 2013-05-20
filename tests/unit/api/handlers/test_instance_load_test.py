from json import loads
import six
from preggy import expect
from tests.unit.base import FullTestCase
from tests.factories import TeamFactory, UserFactory, LoadTestFactory, TestResultFactory
from nose.plugins.attrib import attr
from uuid import uuid4


class InstanceLoadTestsTest(FullTestCase):
    def setUp(self):
        super(InstanceLoadTestsTest, self).setUp()
        self.user = UserFactory.create(with_token=True)
        self.team = TeamFactory.create(owner=self.user)
        self.project = self.team.add_project("schedule-test-project-1", "repo", self.user)
        self.load_test = LoadTestFactory.create(created_by=self.team.owner, team=self.team, project_name=self.project.name)

    @attr('focus')
    def test_get_instance_load_test(self):
        result1 = TestResultFactory.build()
        result2 = TestResultFactory.build()
        self.load_test.results.append(result1)
        self.load_test.results.append(result2)
        self.load_test.save()

        url = '/teams/%s/projects/%s/load_tests/%s' % (self.team.name, self.project.name, self.load_test.uuid)

        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(200)

        obj = response.body
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')

        obj = loads(obj)
        print obj

        result1_last_cycle = result1.cycles[-1]
        result2_last_cycle = result2.cycles[-1]

        expect(obj['uuid']).to_equal(str(self.load_test.uuid))
        expect(obj['results'][0]['uuid']).to_equal(str(result1.uuid))
        expect(obj['results'][0]['concurrent_users']).to_equal(result1_last_cycle.concurrent_users)
        expect(obj['results'][0]['title']).to_equal(result1.config.title)
        expect(obj['results'][0]['requests_per_second']).to_equal(result1_last_cycle.request.successful_requests_per_second)
        expect(obj['results'][0]['failed_requests']).to_equal(result1_last_cycle.request.failed_requests)
        expect(obj['results'][0]['p95']).to_equal(result1_last_cycle.request.p95)

        expect(obj['results'][1]['uuid']).to_equal(str(result2.uuid))
        expect(obj['results'][1]['concurrent_users']).to_equal(result2_last_cycle.concurrent_users)
        expect(obj['results'][1]['title']).to_equal(result2.config.title)
        expect(obj['results'][1]['requests_per_second']).to_equal(result2_last_cycle.request.successful_requests_per_second)
        expect(obj['results'][1]['failed_requests']).to_equal(result2_last_cycle.request.failed_requests)
        expect(obj['results'][1]['p95']).to_equal(result2_last_cycle.request.p95)

    @attr('focus')
    def test_get_instance_load_test_404(self):
        url = '/teams/%s/projects/%s/load_tests/%s' % (self.team.name, self.project.name, uuid4())

        response = self.fetch_with_headers(url)
        expect(response.code).to_equal(404)
