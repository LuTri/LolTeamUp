from rest.models import ChampionMastery
from rest.models import Summoner
from rest.models import ChampionStatic

from rest.models import STATICPOOL

class ChooseToRiot(object):
	def __init__(self, summoners):
		self.summoners = summoners 

	def run(self):
		self.summoners = Summoner.bulk_get_verbose(self.summoners)
		for summoner in self.summoners:
			print "Name: %s" % summoner.name
			print "Top 5 Champs:"
			for mastery in summoner.masteries[:5]:
				print "\tChamp: %s, points: %d, Level: %d" % (mastery.champion.name, mastery.championPoints, mastery.championLevel)
