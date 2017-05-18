#!python2.7 -u

import unittest
from manage_pear import compare

class DeploymentTest(unittest.TestCase):

	def test_compare(self):
		self.assertEqual(compare("1.3.9", "1.3.10"), True)
		self.assertEqual(compare("1.3.91", "1.3.9"), False)
		self.assertEqual(compare("1.3.91", "1.4.0"), True)

if __name__ == "__main__":
	unittest.main()