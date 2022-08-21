import requests
from requests.exceptions import HTTPError

from helper.api_commons import get_headers, parse_username_tokens
from helper.riot_api_constants import MATCH_HISTORY_URL, PREVIOUS_MATCHES
from helper.embed_constants import BLUE_COLOR, RED_COLOR
from discord import Embed
from discord.ext import commands

from typing import Dict, Any


def get_match_history(puuid: str):
	try:
		r = requests.get(PREVIOUS_MATCHES.format(puuid=puuid), headers=get_headers())
		return r.json()
	except HTTPError as e:
		if r.status_code == 403:
			print('Riot API has expired.')
			return


def get_most_recent_game_id(puuid: str):
	return get_match_history(puuid)[0]


def get_match_data_by_game_id(game_id):
	url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{ game_id }'
	r = requests.get(url, headers=get_headers())

	return r.json()


class MatchInfo(commands.Cog):

	def __init__(self, bot, champion_data: Dict[int, Dict[str, Any]]):
		self.bot = bot
		self.champion_data = champion_data

	@commands.Cog.listener()
	async def on_ready(self):
		print('Match History Cog Online')

	@commands.command(name='last-match', help='Displays info about your last game.')
	async def get_last_match_stats(self, context, *username_tokens):
		username, url_friendly_username = parse_username_tokens(username_tokens)

		url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ url_friendly_username }'

		r = requests.get(url, headers=get_headers())
		summoner_id, account_id, account_name, puuid = '', '', '', ''

		try:
			response = r.json()
			summoner_id = response['id']
			account_id = response['accountId']
			account_name = response['name']
			puuid = response['puuid']
		except:
			print('Error fetching username')

		print(f'Using summoner id { summoner_id }, account id { account_id }, account name { account_name }, puuid { puuid }')
		game_id = get_most_recent_game_id(puuid)
		riot_match_data = get_match_data_by_game_id(game_id)

		user_match_data = None
		for participant in riot_match_data['info']['participants']:
			if participant['puuid'] == puuid:
				user_match_data = participant

		team_id = user_match_data['teamId']
		map_side = ('Blue', 'Red')[team_id == 100]

		kills = int(user_match_data["kills"])
		deaths = int(user_match_data["deaths"])
		assists = int(user_match_data["assists"])

		match_message = Embed(color = (BLUE_COLOR, RED_COLOR)[team_id == 100], title=f'Last Match For { account_name }')
		match_message.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/12.15.1/img/champion/{ self.champion_data[user_match_data["championId"]] ["name"] }.png')

		match_message.add_field(name='Map Side', value=map_side, inline=False)
		match_message.add_field(name='Score', value=f'{kills}/{deaths}/{assists}', inline=True)
		match_message.add_field(name='KDA', value=float(kills / deaths))

		# match_message.add_field(name='Items', value='![d](https://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/1402.png)')
		#
		# match_message.set_image(url='https://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/1402.png')
		# match_message.set_image(url='https://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/3020.png')
		# match_message.set_image(url='https://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/3916.png')
		# match_message.set_image(url='https://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/3101.png')
		# match_message.set_image(url='https://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/3340.png')
		# match_message.set_image(url='https://ddragon.leagueoflegends.com/cdn/10.11.1/img/item/1001.png')

		await context.send(embed=match_message)