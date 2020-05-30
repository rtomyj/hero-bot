import requests
from helper.api_commons import get_headers, parse_username_tokens
from discord import Embed, Colour
from discord.ext import commands

from typing import Dict


def get_match_history(username, urlFriendlyUsername):
	url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ urlFriendlyUsername }'

	r = requests.get(url, headers=get_headers())
	json = r.json()

	try:
		accountId = json['accountId']
		url = f'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{ accountId }'

		r = requests.get(url, headers=get_headers())
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
	r = requests.get(url, headers=get_headers())

	return r.json()

class MatchInfo(commands.Cog):

	def __init__(self, championData: Dict[int, str]):
		self.championData = championData

	@commands.command(name='last-match', help='Displays info about your last game.')
	async def get_last_match_stats(self, context, *usernameTokens):
		username, urlFriendlyUsername = parse_username_tokens(usernameTokens)
		summonerId = ''

		url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ urlFriendlyUsername }'
		print(f'Using {url} to get summoner ID')

		r = requests.get(url, headers = get_headers())

		try:
			response = r.json()
			summonerId = response['id']
		except:
			print('Error fetching username')

		gameId = get_most_recent_game_id(username, urlFriendlyUsername)
		riotMatchData = get_match_data_by_game_id(gameId)
		embedMatchData = dict()	# Data structure to hold info for embed

		for participantData in riotMatchData['participantIdentities']:
			if participantData['player']['summonerId'] == summonerId:
				embedMatchData['participantId'] = participantData['participantId']
				embedMatchData['summonerName'] = participantData['player']['summonerName']

		participantData = riotMatchData['participants'][embedMatchData['participantId'] - 1]
		participantStats = participantData['stats']
		embedMatchData['team'] = ('Blue Side', 'Red Side')[participantData['teamId'] == 100 ]
		embedMatchData['championId'] = participantData['championId']
		embedMatchData['kills'] = participantStats['kills']
		embedMatchData['deaths'] = participantStats['deaths']
		embedMatchData['assists'] = participantStats['assists']

		matchMessage = Embed(color=Colour.from_rgb(224, 17, 95), title=f'Last Match For { embedMatchData["summonerName"] }')
		matchMessage.set_thumbnail(url=f'http://ddragon.leagueoflegends.com/cdn/10.3.1/img/champion/{ self.championData[embedMatchData["championId"]]["name"] }.png')
		matchMessage.add_field(name='Team', value=embedMatchData['team'], inline=False)
		matchMessage.add_field(name='Score', value=f'{ embedMatchData["kills"] }/{ embedMatchData["deaths"] }/{ embedMatchData["assists"] }', inline=True)
		matchMessage.add_field(name='KDA', value=float( int(embedMatchData["kills"]) / int(embedMatchData["deaths"]) ))

		await context.send(embed=matchMessage)