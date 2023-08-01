# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import product

base = os.path.dirname(__file__)

class TestProducts(unittest.TestCase):
	def setUp(self):
		pass

	def test_skyrim(self):
		skyrim_code = file(os.path.join(base, 'product_skyrim.html'), 'r').read()
		skyrim = product.parse_page(skyrim_code)
		self.assertEqual("2011-11-11", skyrim['release_date'])
		self.assertEqual("Bethesda Game Studios, Bethesda Softworks", skyrim['organizations'][0]['names']['en'])
		self.assertEqual("The Elder Scrolls V: Skyrim", skyrim['name'])
		self.assertEqual("Japan", skyrim['releases'][3]['region'])
		self.assertEqual('release/2121', skyrim['releases'][3]['link'])
		self.assertEqual("Gaming Fantasy", skyrim['albums'][4]['titles']['en'])
		self.assertEqual("2012-09-12T18:46", skyrim['meta']['added_date'])
		self.assertEqual("https://media.vgm.io/products/78/1387/1387-1347504448.jpg", skyrim['picture_full'])
		self.assertEqual("https://thumb-media.vgm.io/products/78/1387/1387-1347504448.jpg", skyrim['picture_small'])

	def test_witcher(self):
		witcher_code = file(os.path.join(base, 'product_witcher.html'), 'r').read()
		witcher = product.parse_page(witcher_code)
		self.assertEqual("2011-05-17", witcher['release_date'])
		self.assertEqual("The Witcher", witcher['franchises'][0]['names']['en'])
		self.assertEqual("The Witcher 2: Assassins of Kings", witcher['name'])
		self.assertEqual("Wiedźmin 2: Zabójcy królów", witcher['name_real'])
		self.assertEqual(0, len(witcher['releases']))
		self.assertEqual("KK25", witcher['albums'][0]['catalog'])
		self.assertEqual("Efendija", witcher['meta']['edited_user'])
		self.assertEqual(0, len(witcher['organizations']))

	def test_at(self):
		at_code = file(os.path.join(base, 'product_at.html'), 'r').read()
		at = product.parse_page(at_code)
		self.assertEqual('Franchise', at['type'])
		self.assertEqual("Ar tonelico", at['name'])
		self.assertEqual("アルトネリコ", at['name_real'])
		self.assertEqual(4, len(at['titles']))
		self.assertEqual("Ar tonelico: Melody of Elemia", at['titles'][0]['names']['en'])
		self.assertEqual("product/566", at['titles'][0]['link'])
		self.assertEqual("Game", at['titles'][0]['type'])
		self.assertEqual("2010-12-26T03:20", at['meta']['added_date'])
		self.assertTrue('picture_full' not in at)
		two = [at['albums'][32], at['albums'][33]]
		for thing in two:	# two albums released on the same date, hard to sort
			if thing['link'] == 'album/20283':
				self.assertEqual(True, thing['reprint'])

	def test_empty(self):
		im_code = file(os.path.join(base, 'product_empty.html'), 'r').read()
		im = product.parse_page(im_code)
		self.assertEqual("PROJECT IM@S", im['name'])
		self.assertEqual("プロジェクト・アイマス", im['name_real'])
		self.assertEqual(0, len(im['titles']))
		self.assertEqual(0, len(im['albums']))

	def test_ataraxia(self):
		at_code = file(os.path.join(base, 'product_hollowataraxia.html'), 'r').read()
		at = product.parse_page(at_code)
		self.assertEqual("Fate/hollow ataraxia", at['name'])
		self.assertEqual(27, len(at['albums']))
		self.assertEqual(2, len(at['releases']))
		self.assertEqual("2005-10-28", at['releases'][0]['date'])
		self.assertEqual("Fate/hollow ataraxia", at['releases'][0]['names']['en'])
		self.assertEqual("Fate/hollow ataraxia", at['releases'][0]['names']['ja'])
		self.assertEqual("release/2652", at['releases'][0]['link'])

	def test_clannad(self):
		cl_code = file(os.path.join(base, 'product_clannad.html')).read()
		cl = product.parse_page(cl_code)
		self.assertEqual('CLANNAD', cl['name'])
		self.assertTrue('websites' in cl)
		self.assertTrue('Official' in cl['websites'])
		self.assertTrue('Reference' in cl['websites'])
		self.assertEqual(1, len(cl['websites']['Reference']))
		self.assertEqual('MobyGames', cl['websites']['Reference'][0]['name'])
		self.assertEqual('http://www.mobygames.com/game/clannad', cl['websites']['Reference'][0]['link'])

	def test_hack(self):
		hack_code = file(os.path.join(base, 'product_hack.html')).read()
		hack = product.parse_page(hack_code)
		self.assertEqual('.hack//', hack['name'])
		self.assertEqual('Franchise', hack['type'])
		self.assertEqual(".hack//SIGN", hack['titles'][0]['names']['en'])
		self.assertEqual("MACHIDA ~ooedo Express mail Special CD 2001~", hack['albums'][0]['titles']['en'])
		self.assertEqual("OEMM-0025", hack['albums'][0]['catalog'])
		self.assertEqual("doujin", hack['albums'][0]['type'])
		self.assertTrue("Fan Arrange" in hack['albums'][0]['classifications'])
		self.assertEqual('Test description', hack['description'])

	def test_madhouse(self):
		madhouse_code = file(os.path.join(base, 'product_madhouse.html')).read()
		madhouse = product.parse_page(madhouse_code)
		self.assertEqual('MADHOUSE', madhouse['name'])
		self.assertEqual('Meta-franchise', madhouse['type'])
		self.assertEqual("Anime Studios", madhouse['superproduct']['names']['en'])
		self.assertEqual("product/3854", madhouse['superproduct']['link'])
		self.assertEqual("Final Fantasy: Legend of the Crystals", madhouse['subproducts'][0]['names']['en'])
		self.assertEqual("product/177", madhouse['subproducts'][0]['link'])
		self.assertEqual("Animation", madhouse['subproducts'][0]['type'])
		self.assertEqual("1994-02-21", madhouse['subproducts'][0]['date'])
		self.assertEqual("Final Fantasy \"The Wind Chapter\" \"The Fire Chapter\" Soundtrack", madhouse['albums'][0]['titles']['en'])
		self.assertEqual("COCC-11741", madhouse['albums'][0]['catalog'])
		self.assertEqual("anime", madhouse['albums'][0]['type'])

	def test_bandai(self):
		# empty subproducts
		bandai_code = file(os.path.join(base, 'product_bandai.html')).read()
		bandai = product.parse_page(bandai_code)
		self.assertEqual('BANDAI NAMCO Games', bandai['name'])
		self.assertEqual('Meta-franchise', bandai['type'])
		self.assertEqual(0, len(bandai['subproducts']))

	def test_ecco(self):
		# empty title dates
		ecco_code = file(os.path.join(base, 'product_ecco.html')).read()
		ecco = product.parse_page(ecco_code)
		self.assertEqual('Ecco', ecco['name'])
		self.assertEqual('Franchise', ecco['type'])
		self.assertFalse('date' in ecco['titles'][0])

	def test_attack(self):
		# "other" product type
		attack_code = file(os.path.join(base, 'product_attack.html')).read()
		attack = product.parse_page(attack_code)
		self.assertEqual('Attack on Titan', attack['name'])
		self.assertEqual('Franchise', attack['type'])
		self.assertEqual('2015-08-01', attack['titles'][5]['date'])
		self.assertEqual('Other', attack['titles'][5]['type'])

if __name__ == '__main__':
	unittest.main()
