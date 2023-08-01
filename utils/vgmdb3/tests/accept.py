# From https://gist.github.com/samuraisam/2714195
import unittest
from vgmdb.accept import parse_accept_header

class TestParseAcceptHeader(unittest.TestCase):
	def test_parse_accept_header_browser(self):
		accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8,application/json"
		should = [('text/html', {}, 1.0),
		          ('application/xhtml+xml', {}, 1.0),
		          ('application/json', {}, 1.0),
		          ('application/xml', {}, 0.9),
		          ('*/*', {}, 0.8)]
		self.assertEqual(parse_accept_header(accept), should)

	def test_parse_accept_header_smart_client(self):
		accept = "application/vnd.ficture.lightt-v1.1+json"
		should = [('application/json', {'version': 1.1,
		           'vendor': 'vnd.ficture.lightt'}, 1.0)]
		self.assertEqual(parse_accept_header(accept), should)

	def test_parse_accept_header_dumbish_client(self):
		accept = "application/vnd.ficture.lightt-v1.0"
		should = [('application/vnd.ficture.lightt-v1.0', {}, 1.0)]
		self.assertEqual(parse_accept_header(accept), should)

	def test_parse_accept_header_also_dumb_client(self):
		accept = "application/vnd.ficture.lightt"
		should = [('application/vnd.ficture.lightt', {}, 1.0)]
		self.assertEqual(parse_accept_header(accept), should)

	def test_parse_accept_header_dumb_client(self):
		accept = "application/json"
		should = [('application/json', {}, 1.0)]
		self.assertEqual(parse_accept_header(accept), should)

	def test_parse_accept_header_really_dumb_client(self):
		accept = ""
		should = [('', {}, 1.0)]
		self.assertEqual(parse_accept_header(accept), should)

	def test_parse_accept_header_null(self):
		accept = None
		should = []
		self.assertEqual(parse_accept_header(accept), should)


if __name__ == '__main__':
	unittest.main()
