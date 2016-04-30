from rest import RiotApiClient

def import_func(name):
	components = name.split('.')
	mod = __import__(components[0])
	for comp in components[1:]:
		mod = getattr(mod, comp)
	return mod

class LolObjectRelationDescriptor(object):
	def __init__(self, attrname, relation, relation_id_name, is_1tomany):
		self.attrname = attrname
		self._value = None
		self.related_class = relation if not isinstance(relation, basestring)\
			else import_func(relation)
		self.is_1tomany = is_1tomany
		self.relation_id_name = relation_id_name

	def __get__(self, obj, type=None):
		if obj.related_values.get('%s_queried' % self.attrname, None) == None:
			if self.is_1tomany:
				obj.related_values['%s_queried' % self.attrname] =\
					self.related_class.bulk_get(
						getattr(obj, self.relation_id_name))
			else:
				obj.related_values['%s_queried' % self.attrname] =\
					self.related_class.get_one(
						getattr(obj, self.relation_id_name))

		return obj.related_values['%s_queried' % self.attrname]

	def __set__(self, obj, value):
		obj.related_values['%s_queried' % self.attrname] = value

class LolObject(object):
	api_func = NotImplemented
	api_func_multi = NotImplemented

	api_func_verbose = NotImplemented
	api_func_verbose_multi = NotImplemented

	def __new__(cls, *args, **kwargs):
		for relation in cls.Meta.relations:
			setattr(cls, relation[0],
				LolObjectRelationDescriptor(*relation))
		return super(LolObject, cls).__new__(cls, *args, **kwargs)

	def __init__(self, json, recursive=False):
		self.related_values = {}
		for field in self.Meta.fields:
			if isinstance(field, basestring):
				setattr(self, field, json.get(field, None))
			else:
				setattr(self, field[0], json.get(field[0], None))


	class Meta:
		fields = ()
		relations = ()

	@classmethod
	def _query(cls, func_dict={}, params=None):
		get_params = {}
		for field in [field for field in cls.Meta.fields\
				if not isinstance(field, basestring)]:
			get_params.setdefault(*(field[1]))

		client = RiotApiClient()
		query = getattr(client, func_dict['func_name'], None)
		if query:
			if params != None:
				query_params = {func_dict['param_name']:\
					params if not isinstance(params,list) else ','.join(params)}
			else:
				query_params = {}
			result = query(get_params=get_params, **query_params)
			leafs = func_dict.get('leafs')
			if leafs:
				result = reduce(lambda x,y : x[y], [result,] + leafs)
			return result
		else:
			raise AttributeError("No APICall \"%s\" defined!" % func_dict['func_name'])

	@classmethod
	def get_one(cls, params=None, **kwargs):
		if not hasattr(cls, 'pooled'):
			return cls(cls._query(cls.api_func, params))
		else:
			return cls.pooled.find(params)

	@classmethod
	def get_one_verbose(cls, params=None, **kwargs):
		return cls(cls._query(cls.api_func_verbose, params))

	@classmethod
	def _bulk_get(cls, func_dict, params=None, **kwargs):
		objs = []
		result = cls._query(func_dict, params)
		if isinstance(result, list):
			objs = [cls(data) for data in result]
		else:
			objs = [cls(result[key]) for key in result]
		return objs

	@classmethod
	def bulk_get(cls, params=None, **kwargs):
		return cls._bulk_get(cls.api_func_multi, params)

	@classmethod
	def bulk_get_verbose(cls, params=None, **kwargs):
		return cls._bulk_get(cls.api_func_verbose_multi, params)

	@classmethod
	def get_all(cls, **kwargs):
		return cls._bulk_get(cls.api_func_all)

class ChampionStatus(LolObject):
	api_func_all = {
		'func_name': 'champions',
		'param_name': None,
		'leafs':['champions']}

	class Meta(LolObject.Meta):
		fields = (
			'active',
			'botEnabled',
			'botMmEnabled',
			'freeToPlay',
			'id',
			'rankedPlayEnabled'
		)

class ChampionStatic(LolObject):
	api_func_all = {
		'func_name': 'champion_static',
		'param_name': None,
		'leafs': ['data']
	}

	class Meta(LolObject.Meta):
		fields = (
			'id',
			'key',
			'name',
			('tags', ('champData','tags',),),
			'title',
		)

		relations = (
			('status', ChampionStatus, 'id', False,),
		)
