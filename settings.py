API_KEY=NotImplemented
DEFAULT_REGION = 'euw'


try:
	from local_settings import *
except:
	pass

TEAM_CONFIGS = (TEAM_CONFIGS if TEAM_CONFIGS else []) + [
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
