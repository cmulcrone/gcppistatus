import unittest
from gcppistatus.status import *


class StatusTests(unittest.TestCase):

    def testJSON(self):
        ps = status('public')
        self.assertEqual(ps.hello_world(), 'hello world')
        self.assertIsInstance(ps.getJSON('https://status.cloud.google.com/incidents.json')
        , list)
