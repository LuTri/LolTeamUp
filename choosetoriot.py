from rest.models import ChampionMastery
from rest.models import Summoner
from rest.models import ChampionStatic

from rest.models import STATICPOOL
from settings import TEAM_CONFIGS

import messages

class ChooseToRiot(object):
	def __init__(self, summoner_names):
		self.summoner_names = summoner_names
		self.summoners = None
		self.teamed = {
			'winmode': {},
			'trainingmode': {}
		}

	def _request_summoners(self):
		self.summoners = Summoner.bulk_get(self.summoner_names)

	def _tag_summoners(self, reverse):
		summoner_tag_points = {}
		tag_played_by = {}
		tags = dict([(tag, {}) for tag in STATICPOOL.get_distinct_tags()])
		for summoner in self.summoners:
			summoner_tag_points[summoner] = summoner.get_accumulated_tag_points()

		for tag in tags:
			for summoner in summoner_tag_points:
				tags[tag][summoner] = tags[tag].setdefault(summoner, 0)\
					+ summoner_tag_points[summoner][tag]
		
			tags[tag] = sorted(
				tags[tag].keys(),
				key = lambda x: tags[tag][x],
				reverse=reverse)

		for team in TEAM_CONFIGS:
			arranged = []
			tag_played_by[team['configname']] = {}
			try:
				for tag in team['tags']:
					tag_played_by[team['configname']][tag] = [
						summoner for summoner in tags[tag]\
						if summoner.name not in arranged
					][0]

					arranged.append(tag_played_by[team['configname']][tag].name)
			except IndexError:
				pass

		return tag_played_by

	def _train_tags(self):
		result = self._tag_summoners(False)
		print result

	def _win_tags(self):
		result = self._tag_summoners(True)

	def _team_up(self):
		for config in TEAM_CONFIGS:
			self.teamed[config['configname']] = ''
			#TODO: concept on how to team up!!
# 1. T-Config by highest accumulated-point tag in masteries
# 2. T-Config by lowest accumulated-point tag in masteries

	def _make_suggestions(self, summoner):
		next_level_up = summoner.get_next_level_5()
		toptag, two_top_tags = summoner.get_2_suggested_by_top_tag()
		leasttag, two_not_top_tags = summoner.get_2_suggested_by_not_top_tag()
		topaccutag, two_most_accu_tags = summoner.get_2_suggested_by_mastered_tag()
		leastaccutag, tow_least_accu_tags = summoner.get_2_suggested_by_not_mastered_tag()

		print "####### %s, your suggested champs are:" % summoner.name
		print messages.RANDOM_TOP_TAGS % toptag
		for champ in two_top_tags:
			print "\t%s" % champ.name

		print messages.RANDOM_LEAST_TAGS % leasttag
		for champ in two_not_top_tags:
			print "\t%s" % champ.name

	def run(self):
		self._request_summoners()
		for summoner in self.summoners:
			self._make_suggestions(summoner)
