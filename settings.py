API_KEY=NotImplemented
DEFAULT_REGION = 'euw'

TEAM_CONFIGS = [
	{
		'configname': 'STANDARD',
		'tags': [
			'Tank',
			'Fighter',
			'Mage',
			'Support',
			'Marksman',
		]
	}, {
		'configname': 'ADVANCED',
		'tags': [
			'Fighter',
			'Tank',
			'Assassin',
			'Support',
			'Marksman'
		]
	}
]

try:
	from local_settings import *
except:
	pass
