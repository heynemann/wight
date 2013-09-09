import unittest

from funkload.FunkLoadTestCase import FunkLoadTestCase


class ShowTeamTest(FunkLoadTestCase):
    def setUp(self):
        self.server_url = '%s/teams' % (self.conf_get('main', 'url').rstrip('/'),)

    def test_show_team(self):
        self.get("%s/teste" % self.server_url, description='show team url')

if __name__ == '__main__':
    unittest.main()
