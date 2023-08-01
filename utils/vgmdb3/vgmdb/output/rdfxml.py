import sys
import importlib

mimetypes = ['application/rdf+xml']
name = 'rdf'

class outputter(object):
	content_type = 'application/rdf+xml; charset=utf-8'

	def __init__(self, config):
		self._config = config
		if self._config.AUTO_RELOAD and \
                   'vgmdb.output.rdf' in list(sys.modules.keys()):
			importlib.reload(sys.modules['vgmdb.output.rdf'])
		from . import rdf
		self._rdf = rdf

	def __call__(self, type, data, filterkey=None):
		return self._rdf.generate(self._config, type, data).serialize(format="xml")
