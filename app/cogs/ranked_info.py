import requests
from helper.api_commons import get_headers, parse_username_tokens
from discord import Embed, Colour
from discord.ext import commands


class RankedInfo(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.ROMAN_maps_DECIMAL = { 'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5' }
		self.RANK_ICON_URL_TEMPLATE = 'https://opgg-static.akamaized.net/images/medals/%s_%s.png'
		self.EMBED_COLOR = Colour.from_rgb(224, 17, 95)

	def get_ranked_results(self, username, userId, request):
		REQUEST_maps_QUEUE_TYPE = {'solo': 'RANKED_SOLO_5x5', 'flex': 'RANKED_FLEX_SR'}

		r = requests.get(f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{userId}', headers = get_headers())


		foundRankRecord = None
		for rankedQueueInfo in r.json():
			if rankedQueueInfo['queueType'] == REQUEST_maps_QUEUE_TYPE[request]:
				foundRankRecord = rankedQueueInfo

		if foundRankRecord == None:
			raise Exception('No ranked data found for solo queue')

		hotstreak = ''
		if foundRankRecord['hotStreak'] == True:
			hotstreak = 'You are on fire right now! Keep the win streak up.'


		current_rank_info = ( foundRankRecord["tier"].lower(), self.ROMAN_maps_DECIMAL[foundRankRecord["rank"]] )
		current_rank_icon_url = self.RANK_ICON_URL_TEMPLATE % current_rank_info
		print(current_rank_icon_url)

		soloRankRecordEmbed = Embed(color=self.EMBED_COLOR, title=f'Solo/Duo Rank Queue Stats For { username }')
		soloRankRecordEmbed.set_thumbnail( url=current_rank_icon_url )
		soloRankRecordEmbed.add_field(name='Current Rank', value=f'{ foundRankRecord["tier"] } { self.ROMAN_maps_DECIMAL[foundRankRecord["rank"]] } {foundRankRecord["leaguePoints"]}LP', inline=False)
		soloRankRecordEmbed.add_field(name='Total Wins', value=f'{ foundRankRecord["wins"] }', inline=True)
		soloRankRecordEmbed.add_field(name='Total Losses', value=f'{ foundRankRecord["losses"] }', inline=True)
		soloRankRecordEmbed.add_field(name='Win/Loss Ratio', value=f'{ float(int(foundRankRecord["wins"]) / (int(foundRankRecord["wins"]) + int(foundRankRecord["losses"]))) }', inline=True)

		return soloRankRecordEmbed

	@commands.Cog.listener()
	async def on_ready(self):
		print('Rank Cog Online')

	@commands.command(name='rank-solo')
	async def rank_solo(self, context, *usernameTokens):
		username, url_friendly_username = parse_username_tokens(usernameTokens)


		url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ url_friendly_username }'
		print(f'Using {url} to get summoner ID')

		req = requests.get(url, headers = get_headers())

		try:
			response = req.json()
			userId = response['id']

			try:
				print(f'Sending {username} their rank results.')
				await context.send( embed=self.get_ranked_results(username, userId, 'solo') )
				return
			except Exception as e:
				print(f'Error retreiving {username} rank results. Err = { e }')
				await context.send(f'{username} does not have Solo/Duo Rank games.')
				return
		except KeyError as r:
			if r.status_code == 403:
				print('Riot API has expired.')
				await context.send(f'Error connecting to riot servers.')
				return
			elif r.status_code == 404:
				print(f'{username} is not a real user.')
				await context.send(f'{username} is not registered with Riot.')
				return