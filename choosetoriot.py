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
			for mastery in summoner.masteries:
				print "\tChamp: %s, points: %d, Level: %d" % (mastery.champion.name, mastery.championPoints, mastery.championLevel)
			print summoner.get_next_level_5().name
			print len(STATICPOOL.get_not_in_masteries(summoner.masteries))
			print summoner.get_top_played_tags()

			for champ in STATICPOOL.get_not_in_masteries(
					summoner.masteries,
					STATICPOOL.get_by_tag(summoner.get_top_played_tags()[0])
				):
				print champ.name
