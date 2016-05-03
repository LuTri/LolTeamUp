from rest.models import ChampionMastery
from rest.models import Summoner
from rest.models import ChampionStatic

from rest.models import STATICPOOL
from settings import TEAM_CONFIGS

class ChooseToRiot(object):
	def __init__(self, summoner_names):
		self.summoner_names = summoner_names
		self.summoners = None
		self.teamed = None

	def _request_summoners(self):
		self.summoners = Summoner.bulk_get(self.summoner_names)

	def _team_up(self):
		if self.teamed == None:
			self.teamed = {}
		for config in TEAM_CONFIGS:
			self.teamed[config['configname']] = ''
			#TODO: concept on how to team up!!

	def run(self):
		self._request_summoners()
		for summoner in self.summoners:
			print "Next to level: %s" % summoner.get_next_level_5().name

			tag, champs = summoner.get_2_suggested_by_top_tag()
			print "Your top-tag: %s" % tag
			for champ in champs:
				print "\t%s" % champ.name

			tag, champs = summoner.get_2_suggested_by_not_top_tag()
			print "Your least-played tag: %s" % tag
			for champ in champs:
				print "\t%s" % champ.name
