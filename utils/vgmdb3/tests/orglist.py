# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import orglist

base = os.path.dirname(__file__)

class TestOrgList(unittest.TestCase):
	def setUp(self):
		pass

	def test_list(self):
		list_code = file(os.path.join(base, 'orglist.html'), 'r').read()
		list = orglist.parse_page(list_code)

		self.assertEqual(27, len(list(list['orgs'].keys())))
		self.assertEqual("org/442", list['orgs']['#'][0]['link'])
		self.assertEqual("<echo>PROJECT", list['orgs']['#'][0]['names']['en'])
		self.assertEqual(16, len(list['orgs']['#']))
		self.assertEqual("org/860", list['orgs']['#'][-1]['link'])
		self.assertEqual(1, len(list['orgs']['W'][1]['formerly']))
		self.assertEqual("Disneyland Records", list['orgs']['W'][1]['formerly'][0]['names']['en'])
		self.assertEqual("Warner Music Japan", list['orgs']['W'][3]['names']['en'])
		self.assertEqual(3, len(list['orgs']['W'][3]['imprints']))
		self.assertEqual("A'zip Music", list['orgs']['W'][3]['imprints'][0]['names']['en'])
		self.assertEqual("org/95", list['orgs']['W'][3]['subsidiaries'][0]['link'])
		self.assertEqual("org/13", list['orgs']['W'][3]['formerly'][0]['link'])


if __name__ == '__main__':
	unittest.main()
