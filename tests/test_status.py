import unittest
from gcppistatus import *

class StatusTests(unittest.TestCase):

	def testJSON(self):
		self.assertEqual(hello_world(), 'hello world')