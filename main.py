#!/usr/bin/python

from optparse import OptionParser

import settings
from choosetoriot import ChooseToRiot

def run(*args, **kwargs):
	parser = OptionParser()
	parser.add_option("-r", "--region", dest="region")

	options, args = parser.parse_args()
	if len(args) < 1:
		raise RuntimeError("You must at least provide 1 Summoner-Name")
	ctr_client = ChooseToRiot(
		summoner_names=args)
	ctr_client.run()

if __name__ == '__main__':
	try:
		run()
	except Exception as e:
		print e.message
