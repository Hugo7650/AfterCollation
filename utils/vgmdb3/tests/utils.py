# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import utils
from vgmdb.output import commonutils as outpututils

base = os.path.dirname(__file__)

class TestUtils(unittest.TestCase):
	def setUp(self):
		pass

	def test_is_english(self):
		self.assertTrue(utils.is_english("This is a test"))
		self.assertTrue(utils.is_english("Th!s 1s 4 test"))
		self.assertTrue(utils.is_english("Varèse Sarabande"))
		self.assertFalse(utils.is_english("白河ことり"))
		self.assertFalse(utils.is_english("東方人 -TOHO BEAT-"))
		self.assertTrue(utils.is_english("Marcin Przybyłowicz"))

	def test_date_parse(self):
		date = "Aug 3, 2006 09:33 AM"
		self.assertEqual("2006-08-03T09:33", utils.parse_date_time(date))
		date = "Aug 3, 2006 12:33 PM"
		self.assertEqual("2006-08-03T12:33", utils.parse_date_time(date))
		date = "Oct 04, 2000"
		self.assertEqual("2000-10-04", utils.parse_date_time(date))
		date = "November 11, 2011"
		self.assertEqual("2011-11-11", utils.parse_date_time(date))
		date = "Sep, 2011"
		self.assertEqual("2011-09", utils.parse_date_time(date))
		date = "Oct 2011"
		self.assertEqual("2011-10", utils.parse_date_time(date))
		date = "October 2011"
		self.assertEqual("2011-10", utils.parse_date_time(date))
		date = "2011"
		self.assertEqual("2011", utils.parse_date_time(date))
		date = "Jan 7"
		self.assertEqual("0000-01-07", utils.parse_date_time(date))
		date = "Dec, 9"
		self.assertEqual("0000-12-09", utils.parse_date_time(date))
		date = "0"
		self.assertEqual(None, utils.parse_date_time(date))
		date = "Dec 5 1791"
		self.assertEqual("1791-12-05", utils.parse_date_time(date))

	def test_dotted_year(self):
		""" Make sure that weird dates with unknown month and days work """
		date = utils.normalize_dotted_date("2007.??.??")
		self.assertEqual("2007", date)
	def test_dotted_month(self):
		""" Make sure that weird dates with unknown days work """
		date = utils.normalize_dotted_date("2007.02.??")
		self.assertEqual("2007-02", date)
	def test_dotted_day(self):
		""" Make sure that conversion from YYYY.MM.DD to YYYY-MM-DD works """
		date = utils.normalize_dotted_date("2007.02.20")
		self.assertEqual("2007-02-20", date)
	def test_dotted_shortday(self):
		""" Make sure that conversion from YYYY.M.D to YYYY-MM-DD works """
		date = utils.normalize_dotted_date("2007.2.9")
		self.assertEqual("2007-02-09", date)
	def test_dashed_shortmonth(self):
		""" Make sure that conversion from YYYY.M.D to YYYY-MM-DD works """
		date = utils.normalize_dashed_date("2007-2")
		self.assertEqual("2007-02", date)

	def test_invalid_html(self):
		invalid = '<table><tr></tr><table five>asdf</table><table>'
		correct = '<table><tr></tr></table><table five>asdf</table><table>'
		self.assertEqual(correct, utils.fix_invalid_table(invalid))
		invalid = '<table><tr><tr></tr></table>'
		correct = '<table><tr></tr></table>'
		self.assertEqual(correct, utils.fix_invalid_table(invalid))
		invalid = '<table><tr></tr></tr></table>'
		correct = '<table><tr></tr></table>'
		self.assertEqual(correct, utils.fix_invalid_table(invalid))

	def test_languagecodes(self):
		tests = {
		    'Japanese':'ja',
		    'Japanese 1':'ja',
		    'Korean, Chinese':'ko-zd',
		    'English':'en',
		    'English iTunes':'en',
		    'English Gaelic':'gd',
		    'Gaelic':'gd'
		}
		for test,expected in list(tests.items()):
			got = outpututils.normalize_language_codes(test)
			self.assertEqual(expected, got)

class TestLinks(unittest.TestCase):
	def test_trim_absolute(self):
		self.assertEqual('album/29', utils.trim_absolute('http://vgmdb.net/album/29'))
		self.assertEqual('album/29', utils.trim_absolute('https://vgmdb.net/album/29'))
		self.assertEqual('http://wikipedia.org/album/29', utils.trim_absolute('http://wikipedia.org/album/29'))
		self.assertEqual('https://wikipedia.org/album/29', utils.trim_absolute('https://wikipedia.org/album/29'))

	def test_force_absolute(self):
		self.assertEqual('https://vgmdb.net/album/29', utils.force_absolute('album/29'))
		self.assertEqual('http://wikipedia.org/album/29', utils.force_absolute('http://wikipedia.org/album/29'))
		self.assertEqual('https://www.facebook.com/akadress', utils.force_absolute('https://www.facebook.com/akadress'))

	def test_parse_vgmdb_link(self):
		self.assertEqual('album/29', utils.parse_vgmdb_link('/album/29'))
		self.assertEqual('album/29', utils.parse_vgmdb_link('album/29'))
		self.assertEqual('release/29', utils.parse_vgmdb_link('db/release.php?id=29'))

	def test_strip_redirect(self):
		self.assertEqual('http://www.mobygames.com/game/clannad', utils.strip_redirect('https://vgmdb.net/redirect/43446/www.mobygames.com/game/clannad'))
		self.assertEqual('http://www.mobygames.com/game/clannad', utils.strip_redirect('/redirect/43446/www.mobygames.com/game/clannad'))
		self.assertEqual('http://www.mobygames.com/game/clannad', utils.strip_redirect('/redirect/0/www.mobygames.com/game/clannad'))
		self.assertEqual('https://www.facebook.com/akadress', utils.strip_redirect('/redirect/63221/https://www.facebook.com/akadress'))
		self.assertEqual('http://musenote.blog10.fc2.com/blog-entry-187.html', utils.strip_redirect('/redirect/79973/vgmdb.net/redirect/79964/musenote.blog10.fc2.com/blog-entry-187.html'))

	def test_media(self):
		style = "background-image: url('https://medium-media.vgm.io/albums/97/79/79-1264618929.png')"
		medium = "https://medium-media.vgm.io/albums/97/79/79-1264618929.png"
		thumb = "https://thumb-media.vgm.io/albums/97/79/79-1264618929.png"
		full = "https://media.vgm.io/albums/97/79/79-1264618929.png"
		self.assertEqual(medium, utils.extract_background_image(style))
		self.assertEqual(thumb, utils.media_thumb(medium))
		self.assertEqual(full, utils.media_full(medium))

if __name__ == '__main__':
	unittest.main()
