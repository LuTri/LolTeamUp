from rest import RiotApiClient
from datetime import datetime
import time
import random

random.seed(int(time.mktime(datetime.now().timetuple())))

def import_func(clsname):
	if isinstance(clsname, basestring):
		components = clsname.split('.')
		mod = __import__(components[0])
		for comp in components[1:]:
			mod = getattr(mod, comp)
		return mod
	else:
		return clsname

class LolObjectRelationDescriptor(object):
	def __init__(self, attrname, relation, relation_id_name, is_1tomany):
		self.attrname = attrname
		self._value = None
		self.related_class = import_func(relation)
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

	def __init__(self, json):
		self.related_values = {}
		for field in self.Meta.fields:
			if isinstance(field, basestring):
				setattr(self, field, json.get(field, None))
			else:
				data = reduce(lambda x,y : x[y], [json,] + field['leafs'])
				data = import_func(field['model'])(data) if field['model'] else data
				setattr(self, field['attr'], data)

	class Meta:
		fields = ()
		relations = ()

class QueriedLolObject(LolObject):
	@classmethod
	def _query(cls, func_dict={}, params=None):
		get_params = {}
		for field in [field for field in cls.Meta.fields\
				if not isinstance(field, basestring)]:
			get_params.update(field['get_params'])

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

class ChampionStatus(QueriedLolObject):
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

class ChampionStatic(QueriedLolObject):
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
			{
				'attr': 'tags',
				'leafs': ['tags'],
				'model': None,
				'get_params': {'champData': 'tags'}
			},
			'title',
		)

		relations = (
			('status', ChampionStatus, 'id', False,),
		)

class ChampionMastery(QueriedLolObject):
	api_func = {
		'func_name': 'championmastery_by_player',
		'param_name': 'playerid'}

	api_func_multi = {
		'func_name': 'championmastery_by_player',
		'param_name': 'playerid'}

	class Meta(LolObject.Meta):
		fields = (
			'championLevel',
			'chestGranted',
			'championPoints',
			'championPointsSinceLastLevel',
			'highestGrade',
			'championPointsUntilNextLevel',
			'lastPlayTime',
			'championId',
			'playerId',
		)

		relations = (
			('champion', ChampionStatic, 'championId', False,),
		)

class Summoner(QueriedLolObject):
	api_func_multi = {
		'func_name': 'summoner_by_name',
		'param_name': 'summonernames'}

	class Meta(LolObject.Meta):
		fields = (
			'profileIconId',
			'summonerLevel',
			'revisionDate',
			'id',
			'name',
		)

		relations = (
			('masteries', 'rest.models.ChampionMastery', 'id', True,),
			('recent_games', 'rest.models.Game', 'id', True,),
		)

	def __init__(self, *args, **kwargs):
		self._masteredtags = None
		self._accumulatdtags = None
		self._orderedaccumulatedtags = None
		super(Summoner, self).__init__(*args, **kwargs)

	def get_next_level_5(self):
		try:
			return [entry for entry in\
					sorted(
						self.masteries,
						key=lambda x: x.championPoints,
						reverse=True)
					if entry.championLevel < 5
				][0].champion
		except IndexError:
			return None

	def _get_top_tags(self, champions):
			result = {}
			for champ in champions:
				for tag in champ.tags:
					result[tag] = result.setdefault(tag, 0) + 1

			return sorted(
				[tag for tag in result.keys()],
				key=lambda x: result[x],
				reverse=True)

	def get_accumulated_tag_points(self):
		if self._accumulatdtags == None:
			self._accumulatdtags = dict([(tag, 0) for tag in\
				STATICPOOL.get_distinct_tags()])
			for m in self.masteries:
				for tag in m.champion.tags:
					self._accumulatdtags[tag] = self._accumulatdtags[tag]\
						+ m.championPoints

		return self._accumulatdtags

	def get_tags_ordered_by_accumulated_points(self):
		if self._orderedaccumulatedtags == None:
			tags = self.get_accumulated_tag_points()
			self._orderedaccumulatedtags = sorted(
				tags.keys(),
				key=lambda x: tags[x],
				reverse=True)
		return self._orderedaccumulatedtags

	def get_most_mastered_tags(self):
		if self._masteredtags == None:
			self._masteredtags = self._get_top_tags(
				[m.champion for m in self.masteries])
		return self._masteredtags

	def get_n_suggested_by_tag(self, tag, n, inmasteries=None):
		result = []
		if inmasteries == True:
			valid = STATICPOOL.get_by_tag(tag, valid=STATICPOOL.get_in_masteries(self.masteries))
		elif inmasteries == False:
			valid = STATICPOOL.get_by_tag(tag, valid=STATICPOOL.get_not_in_masteries(self.masteries))
		elif inmasteries == None:
			valid = STATICPOOL.get_by_tag(tag)

		for i in range(0,n if len(valid) > n else len(valid)):
			result.append(valid.pop(random.randint(0,len(valid)-1)))
		return result

	def get_2_suggested_by_top_tag(self):
		tag = self.get_most_mastered_tags()[0]
		return tag, self.get_n_suggested_by_tag(tag, 2, True)

	def get_2_suggested_by_not_top_tag(self):
		tag = self.get_most_mastered_tags()[-1]
		return tag, self.get_n_suggested_by_tag(tag, 2, True)

	def get_2_suggested_by_mastered_tag(self):
		tag = self.get_tags_ordered_by_accumulated_points()[0]
		return tag, self.get_n_suggested_by_tag(tag, 2, True)

	def get_2_suggested_by_not_mastered_tag(self):
		tag = self.get_tags_ordered_by_accumulated_points()[-1]
		return tag, self.get_n_suggested_by_tag(tag, 2, True)

class Game(QueriedLolObject):
	api_func_multi = {
		'func_name': 'game_by_player_id',
		'param_name': 'playerid',
		'leafs': ['games',]}

	class Meta(LolObject.Meta):
		fields = (
			'championId',
			{
				'attr': 'stats',
				'leafs': ['stats'],
				'model': 'rest.models.GameStats',
				'get_params': {}
			}
		)

		relations = (
			('champion', ChampionStatic, 'championId', False,),
		)

class GameStats(LolObject):
	class Meta(LolObject.Meta):
		fields = (
			'assists',
			'championsKilled',
			'goldEarned',
			'goldSpent',
			'item0',
			'item1',
			'item2',
			'item3',
			'item4',
			'item5',
			'item6',
			'killingSprees',
			'largestKillingSpree',
			'largestMultiKill',
			'level',
			'magicDamageDealtPlayer',
			'magicDamageDealtToChampions',
			'magicDamageTaken',
			'minionsKilled',
			'numDeaths',
			'physicalDamageDealtPlayer',
			'physicalDamageDealtToChampions',
			'physicalDamageTaken',
			'playerPosition',
			'playerRole',
			'team',
			'timePlayed',
			'totalDamageDealt',
			'totalDamageDealtToChampions',
			'totalDamageTaken',
			'totalHeal',
			'totalTimeCrowdControlDealt',
			'totalUnitsHealed',
			'trueDamageDealtPlayer',
			'trueDamageDealtToChampions',
			'trueDamageTaken',
			'win',
		)

class LolObjectPool(object):
	instance = NotImplemented
	model = None

	class _Singleton(object):
		def __init__(self, cls):
			self.model = cls.model
			self.index = cls.index
			self._load()

		def _load(self):
			self._modelinstances = self.model.get_all()

		def find(self, value):
			for item in self._modelinstances:
				if getattr(item, self.index, None) == value:
					return item
			raise IndexError("ModelInstance with \"%s\" = \"%s\" not found!" % (
				attrname,
				value
			))

	def __new__(cls, *args, **kwargs):
		if cls.instance == None:
			cls.instance = cls._Singleton(cls, *args, **kwargs)
			setattr(cls.model, 'pooled', cls.instance)

		return cls.instance

class ChampionStatusPool(LolObjectPool):
	instance = None
	model = ChampionStatus
	index = 'id'

class ChampionStaticPool(LolObjectPool):
	instance = None
	model = ChampionStatic
	index = 'id'

	class _Singleton(LolObjectPool._Singleton):
		def __init__(self, *args, **kwargs):
			self._distincttags = None
			super(ChampionStaticPool._Singleton, self).__init__(*args, **kwargs)

		def get_distinct_tags(self):
			if self._distincttags == None:
				self._distincttags = set()
				for champ in self._modelinstances:
					for tag in champ.tags:
						self._distincttags.add(tag)
			return self._distincttags

		def get_by_tag(self, tag, valid=None):
			return [champ for champ in self._modelinstances\
				if tag in champ.tags\
				and (champ in valid if valid else True)]

		def get_not_in_masteries(self, masteries, valid=None):
			return [champ for champ in self._modelinstances\
				if champ not in [m.champion for m in masteries]\
				and (champ in valid if valid else True)]

		def get_in_masteries(self, masteries, valid=None):
			return [champ for champ in self._modelinstances\
				if champ in [m.champion for m in masteries]\
				and (champ in valid if valid else True)]

STATICPOOL = ChampionStaticPool()
STATUSPOOL = ChampionStatusPool()
