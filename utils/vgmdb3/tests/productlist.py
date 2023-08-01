# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import productlist

base = os.path.dirname(__file__)

class TestProductList(unittest.TestCase):
	def setUp(self):
		pass

	def test_list(self):
		list_code = file(os.path.join(base, 'productlist.html'), 'r').read()
		list = productlist.parse_page(list_code)

		self.assertEqual("product/856", list['products'][0]['link'])
		self.assertEqual("Darius", list['products'][0]['names']['en'])
		self.assertEqual("Franchise", list['products'][0]['type'])
		self.assertEqual(30, len(list['products']))


if __name__ == '__main__':
	unittest.main()
