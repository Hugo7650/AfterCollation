# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb.parsers import orglist
from vgmdb.config import BASE_URL
from urllib.parse import urljoin

class TestOrglistRDF(TestRDF):
	data_parser = lambda self,x: orglist.parse_page(x)
	outputter_type = 'orglist'
	def setUp(self):
		pass

	def run_list_tests(self, graph):
		test_count_results = {
			"select ?org where { ?org rdf:type schema:Organization . }" : 1181,
			"select ?org where { ?org rdf:type foaf:Organization . }" : 1181,
			"select ?title where { <@baseorg/529#subject> schema:name ?title . }" : 1,
			"select ?title where { <@baseorg/203#subject> schema:name ?title . }" : 1
		}
		test_first_result = {
			"select ?name where { <@baseorg/529#subject> foaf:name ?name . }" : "Studio Ghibli Records",
			"select ?name where { <@baseorg/529#subject> schema:name ?name . }" : "Studio Ghibli Records",
			"select ?name where { <@baseorg/203#subject> foaf:name ?name . }" : "VAGRANCY",
			"select ?name where { <@baseorg/203#subject> schema:name ?name . }" : "VAGRANCY",
		}
		self.run_tests(graph, test_count_results, test_first_result)
	def run_list_tests_S(self, graph):
		test_count_results = {
			"select ?org where { ?org rdf:type schema:Organization . }" : 172,
			"select ?org where { ?org rdf:type foaf:Organization . }" : 172,
			"select ?title where { <@baseorg/529#subject> schema:name ?title . }" : 1,
			"select ?title where { <@baseorg/203#subject> schema:name ?title . }" : 0
		}
		test_first_result = {
			"select ?name where { <@baseorg/529#subject> foaf:name ?name . }" : "Studio Ghibli Records",
			"select ?name where { <@baseorg/529#subject> schema:name ?name . }" : "Studio Ghibli Records"
		}
		self.run_tests(graph, test_count_results, test_first_result)
	def run_list_tests_V(self, graph):
		test_count_results = {
			"select ?org where { ?org rdf:type schema:Organization . }" : 20,
			"select ?org where { ?org rdf:type foaf:Organization . }" : 20,
			"select ?title where { <@baseorg/529#subject> schema:name ?title . }" : 0,
			"select ?title where { <@baseorg/203#subject> schema:name ?title . }" : 1
		}
		test_first_result = {
			"select ?name where { <@baseorg/203#subject> foaf:name ?name . }" : "VAGRANCY",
			"select ?name where { <@baseorg/203#subject> schema:name ?name . }" : "VAGRANCY",
		}
		self.run_tests(graph, test_count_results, test_first_result)
	def test_list_rdfa_S(self):
		graph = self.load_rdfa_data('orglist.html', 'S')
		self.run_list_tests_S(graph)
	def test_list_rdfa_V(self):
		graph = self.load_rdfa_data('orglist.html', 'V')
		self.run_list_tests_V(graph)
	def test_list_rdfa(self):
		graph = self.load_rdfa_data('orglist.html')
		self.run_list_tests(graph)
	def test_list_rdf(self):
		graph = self.load_rdf_data('orglist.html')
		self.run_list_tests(graph)


if __name__ == '__main__':
	unittest.main()
