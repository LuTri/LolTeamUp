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
}
