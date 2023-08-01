# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb.parsers import search
from vgmdb.config import BASE_URL
from urllib.parse import urljoin

class TestSearchRDF(TestRDF):
	data_parser = lambda self,x: search.parse_page(x)
	outputter_type = 'search'
	def setUp(self):
		pass

	def run_list_tests(self, graph):
		test_count_results = {
			"select ?search where { ?search rdf:type schema:MusicAlbum . }" : 8,
			"select ?search where { ?search rdf:type mo:Release . }" : 8,
			"select ?search where { ?search rdf:type schema:MusicGroup . }" : 1,
			"select ?search where { ?search rdf:type foaf:Organization . }" : 1,
			"select ?search where { ?search rdf:type schema:Organization . }" : 1,
			"select ?search where { ?search rdf:type schema:CreativeWork . }" : 1
		}
		test_first_result = {
			"select ?name where { <@basealbum/15634#subject> dcterms:title ?name . FILTER(lang(?name)='en') }" : "Vagrant Story Original Soundtrack",
			"select ?name where { <@basealbum/15634#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "Vagrant Story Original Soundtrack",
			"select ?name where { <@baseartist/7195#subject> foaf:name ?name . FILTER(lang(?name)='en') }" : "Samuel Day",
			"select ?name where { <@baseorg/203#subject> foaf:name ?name . FILTER(lang(?name)='en') }" : "VAGRANCY",
			"select ?name where { <@baseorg/203#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "VAGRANCY",
			"select ?name where { <@baseproduct/427#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "Vagrant Story",
			"select ?name where { <@baseproduct/427#subject> dcterms:title ?name . FILTER(lang(?name)='en') }" : "Vagrant Story"
		}
		self.run_tests(graph, test_count_results, test_first_result)
	def test_list_rdfa(self):
		graph = self.load_rdfa_data('search.html')
		self.run_list_tests(graph)
	def test_list_rdf(self):
		graph = self.load_rdf_data('search.html')
		self.run_list_tests(graph)


if __name__ == '__main__':
	unittest.main()
