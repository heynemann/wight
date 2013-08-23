from tests.factories import TeamFactory, LoadTestFactory
from tests.unit.base import WorkerTestCase


class TestBenchConfiguration(WorkerTestCase):

    def test_can_git_clone_in_specific_branch(self):
        team = TeamFactory.create()
        TeamFactory.add_projects(team, 1)
        user = team.owner
        project = team.projects[0]
        load_test = LoadTestFactory.add_to_project(1, user=user, team=team, project=project)
