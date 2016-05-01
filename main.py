#!/usr/bin/python

from optparse import OptionParser

import settings
from choosetoriot import ChooseToRiot

def run(*args, **kwargs):
	parser = OptionParser()
	parser.add_option("-r", "--region", dest="region")

	options, args = parser.parse_args()
	ctr_client = ChooseToRiot(
		summoners=args)
	ctr_client.run()

if __name__ == '__main__':
	run()
