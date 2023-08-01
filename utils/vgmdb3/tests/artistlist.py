# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import artistlist

base = os.path.dirname(__file__)

class TestArtistList(unittest.TestCase):
	def setUp(self):
		pass

	def test_list(self):
		list_code = file(os.path.join(base, 'artistlist.html'), 'r').read()
		list = artistlist.parse_page(list_code)

		self.assertEqual(99, len(list['artists']))
		self.assertEqual("artist/3535", list['artists'][0]['link'])
		self.assertEqual("artist/12702", list['artists'][3]['link'])
		self.assertEqual("artist/11699", list['artists'][96]['link'])
		self.assertEqual("A BONE", list['artists'][0]['names']['en'])
		self.assertEqual("アービー", list['artists'][3]['name_real'])


if __name__ == '__main__':
	unittest.main()
