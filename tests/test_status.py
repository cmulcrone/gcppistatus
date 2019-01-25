import unittest
from gcppistatus.status import *


class StatusTests(unittest.TestCase):

    def testJSON(self):
        url = 'https://status.cloud.google.com/incidents.json'
        ps = status('public', url)
        # self.assertEqual(ps.hello_world(), 'hello world')
        self.assertIsInstance(ps.getJSON(), list)

    def testSeverity(self):
        url = 'https://status.cloud.google.com/incidents.json'
        ps = status('public', url)
        json = ps.getJSON()
        self.assertGreater(ps.calculateSeverity(json), 0)

    def testConnectivityError(self):
        url = 'https://status.cloud.google.com/incidents.jso'
        ps = status('public', url)
        self.assertEquals(ps.getJSON(), 'Error Decoding JSON')
