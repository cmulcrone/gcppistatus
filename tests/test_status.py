import unittest
from gcppistatus.status import *

class StatusTests(unittest.TestCase):

	def testJSON(self):
		js = jsonstatus()
		self.assertEqual(js.hello_world(), 'hello world')
