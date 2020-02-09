import requests
from . import api_commons


def get_match_history(username, urlFriendlyUsername):
	url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ urlFriendlyUsername }'

	r = requests.get(url, headers=api_commons.get_headers())
	json = r.json()

	try:
		accountId = json['accountId']
		url = f'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{ accountId }'

		r = requests.get(url, headers=api_commons.get_headers())
		return r.json()['matches']

	except KeyError as exception:
		if r.status_code == 403:
			print('Riot API has expired.')
			return
		elif r.status_code == 404:
			print(f'{username} is not a real user.')
			return




def get_most_recent_game_id(username, urlFriendlyUsername):
	matches = get_match_history(username, urlFriendlyUsername)
	return matches[0]['gameId']




def get_match_data_by_game_id(gameId):
	url = f'https://na1.api.riotgames.com/lol/match/v4/matches/{ gameId }'
	r = requests.get(url, headers=api_commons.get_headers())

	return r.json()