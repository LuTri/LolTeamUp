MOST_COVERAGE = ['br', 'eune', 'euw', 'lan', 'las', 'na', 'oce', 'ru', 'tr',]
REGION_PBE = ['pbe',]
REGION_JPKR = ['jp', 'kr',]

REGION_COVERAGE = {
	'minimum': MOST_COVERAGE,
	'no_jp': MOST_COVERAGE + REGION_PBE,
	'no_pbe': MOST_COVERAGE + REGION_JPKR,
	'full': MOST_COVERAGE + REGION_PBE + REGION_JPKR,
}

REGION_PLATFORM = {
	'br': 'BR1',
	'eune': 'EUN1',
	'euw': 'EUW1',
	'jp': 'JP1',
	'kr': 'KR',
	'lan': 'LA1',
	'las': 'LA2',
	'na': 'NA1',
	'oce': 'OC1',
	'tr': 'TR1',
	'ru': 'RU',
	'pbe': 'PBE1',
}



ROOT_URL = "https://%(region)s.api.pvp.net"

API_MAPPINGS = {
	'champions': {
		'path': ROOT_URL + '/api/lol/%(region)s/v1.2/champion',
		'coverage': 'no_pbe',
	},
	'championmastery_by_player': {
		'path': ROOT_URL + '/championmastery/location/%(platformid)s/player/%(playerid)s/champions',
		'coverage': 'no_pbe',
	},
	'champion_static': {
		'path': (ROOT_URL % {'region': 'global'}) + '/api/lol/static-data/%(region)s/v1.2/champion',
		'coverage': 'full',
	},
	'summoner_by_name': {
		'path': ROOT_URL + '/api/lol/%(region)s/v1.4/summoner/by-name/%(summonernames)s',
		'coverage': 'no_pbe',
	},
	'summoner_by_id': {
		'path': ROOT_URL + '/api/lol/%(region)s/v1.4/summoner/%(summonerids)s',
		'coverage': 'no_pbe',
	},
	'game_by_player_id': {
		'path': ROOT_URL + '/api/lol/%(region)s/v1.3/game/by-summoner/%(playerid)s/recent',
		'coverage': 'no_pbe'
	},
}
