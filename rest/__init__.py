import types
import json
from datetime import datetime

import requests
import mapping

import settings
from os import path


class RiotApiClient(object):
	class ApiCallDescriptor(object):
		def __init__(self, client, mapping, func_name, cached):
			self.path = mapping['path']
			self.coverage = mapping['coverage']
			self.client = client
			self.cached = cached
			self.func_name = func_name

		def _check_coverage(self, region):
			allowed_regions = mapping.REGION_COVERAGE[self.coverage]
			assert region in allowed_regions,\
				"Region \"%s\" is not covered by this APIEndpoint!" % region

		def _fill_api_args(self, **apiargs):
			apiargs.setdefault('region', self.client.region)
			apiargs.update({'platformid': mapping.REGION_PLATFORM[apiargs['region']]})
			return apiargs

		def _make_cachefile_name(self, **kwargs):
			return '%s.json' %\
				'_'.join(
					[datetime.now().strftime('%Y%m%d%H')] +\
					['%s' % kwargs[key] for key in sorted(kwargs.keys())] +\
					[self.func_name,])\
				.replace(',','_')\
				.replace('.','_')

		def _load_file(self, filename):
			data = None
			if path.isfile(filename):
				with open(filename,'r') as f:
					data = json.load(f)
			return data
		def _save_file(self, filename, data):
			if not path.isfile(filename):
				with open(filename,'w') as f:
					json.dump(data, f)

		def __call__(self, region=None, get_params={}, *args, **kwargs):
			region = region or self.client.region
			self._check_coverage(region)
			if self.cached:
				filename = self._make_cachefile_name(**kwargs)
				result = self._load_file(filename) or self.client.query(
					self.path % self._fill_api_args(region=region,**kwargs),
					**get_params
				)
				self._save_file(filename,result)
			else:
				result = self.client.query(
					self.path % self._fill_api_args(region=region,**kwargs),
					**get_params
				)
			return result

	def __init__(self, region=None, cached=True):
		self.region = region or settings.DEFAULT_REGION
		self.api_key = settings.API_KEY

		for key in mapping.API_MAPPINGS:
			setattr(self, key, self.ApiCallDescriptor(
				client= self,
				mapping=mapping.API_MAPPINGS[key],
				func_name=key,
				cached=cached))

	def _build_params(self, *args, **kwargs):
		new_kwargs = {}
		new_kwargs.update(kwargs)
		new_kwargs.setdefault('api_key', self.api_key)
		return new_kwargs

	def _query(self, path, **kwargs):
		return requests.get(path, params=self._build_params(**kwargs))

	def query(self, path, **kwargs):
		response = self._query(path,**kwargs)
		if response.status_code == 200:
			return json.loads(
				response.text
			)
		else:
			raise RuntimeError("API returned %d!\nresponse: %s\nurl: %s\nHeaders: %s" % (
				response.status_code,
				response.text,
				response.url,
				response.headers
			))
