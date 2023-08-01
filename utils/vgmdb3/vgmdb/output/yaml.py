

mimetypes = ['text/yaml', 'text/x-yaml',
             'application/yaml', 'application/x-yaml']
name = 'yaml'

class outputter(object):
	content_type = 'application/x-yaml; charset=utf-8'

	def __init__(self, config):
		self._config = config
		import yaml
		self._yaml = yaml

	def __call__(self, type, data, filterkey=None):
		return self._yaml.safe_dump(data, allow_unicode=True, default_flow_style=False)
