import requests
from requests.exceptions import HTTPError

from helper.api_commons import get_headers, parse_username_tokens
from helper.riot_abstractions import get_account_info_using_summoner_name
from helper.riot_api_constants import MATCH_HISTORY_URL
from helper.embed_constants import BLUE_COLOR, RED_COLOR
from discord import Embed, Colour
from discord.ext import commands

from typing import Dict


def get_match_history(username, urlFriendlyUsername):
	try:
		accountId = get_account_info_using_summoner_name(urlFriendlyUsername)

		r = requests.get(MATCH_HISTORY_URL.format(accountId = accountId), headers=get_headers())
		return r.json()['matches']
	except HTTPError as e:
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

		participantId = None
		summonerName = None
		for participantData in riotMatchData['participantIdentities']:
			if participantData['player']['summonerId'] == summonerId:
				participantId= participantData['participantId']
				summonerName = participantData['player']['summonerName']

		participantData = riotMatchData['participants'][participantId - 1]
		mapSide = ('Blue', 'Red')[participantData['teamId'] == 100 ]

		participantStats = participantData['stats']
		kills = int(participantStats["kills"])
		deaths = int(participantStats["deaths"])
		assists = int(participantStats["assists"] )


		matchMessage = Embed(color= (BLUE_COLOR, RED_COLOR)[participantData['teamId'] == 100 ], title=f'Last Match For { summonerName }')
		matchMessage.set_thumbnail(url=f'http://ddragon.leagueoflegends.com/cdn/10.3.1/img/champion/{ self.championData[participantData["championId"]] ["name"] }.png')

		matchMessage.add_field(name = 'Map Side', value = mapSide, inline = False)
		matchMessage.add_field(name='Score', value=f'{kills}/{deaths}/{assists}', inline=True)
		matchMessage.add_field(name='KDA', value=float(kills / deaths))
		matchMessage.add_field(name = 'Items', value = '![](http://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/1402.png)')

		matchMessage.set_image(url = 'http://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/1402.png')
		matchMessage.set_image(url = 'http://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/3020.png')
		matchMessage.set_image(url = 'http://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/3916.png')
		matchMessage.set_image(url = 'http://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/3101.png')
		matchMessage.set_image(url = 'http://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/3340.png')
		# matchMessage.set_image(url = 'http://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/1001.png')

		print(f'Sending {username} their stats for the last game they played.')
		await context.send(embed=matchMessage)