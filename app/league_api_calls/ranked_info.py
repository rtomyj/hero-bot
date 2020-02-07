import requests
from . import api_commons
from discord import Embed, Colour
from discord.ext import commands


bot = commands.Bot(command_prefix='!')



def get_ranked_results(username, userId, request):
	REQUEST_maps_QUEUE_TYPE = {'solo': 'RANKED_SOLO_5x5', 'flex': 'RANKED_FLEX_SR'}

	r = requests.get(f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{userId}', headers = api_commons.get_headers())



	foundRankRecord = None
	for rankedQueueInfo in r.json():
		if rankedQueueInfo['queueType'] == REQUEST_maps_QUEUE_TYPE[request]:
			foundRankRecord = rankedQueueInfo

	if foundRankRecord == None:
		raise Exception('No ranked data found for solo queue')

	hotstreak = ''
	if foundRankRecord['hotStreak'] == True:
		hotstreak = 'You are on fire right now! Keep the win streak up.'

	soloRankRecordEmbed = Embed(color=Colour.from_rgb(224, 17, 95), title=f'Solo/Duo Rank Queue Stats For { username }')
	soloRankRecordEmbed.add_field(name='Current Rank', value=f'{ foundRankRecord["tier"] } { foundRankRecord["rank"] } {foundRankRecord["leaguePoints"]}LP', inline=False)
	soloRankRecordEmbed.add_field(name='Total Wins', value=f'{ foundRankRecord["wins"] }', inline=True)
	soloRankRecordEmbed.add_field(name='Total Losses', value=f'{ foundRankRecord["losses"] }', inline=True)
	soloRankRecordEmbed.add_field(name='Win/Loss Ratio', value=f'{ float(int(foundRankRecord["wins"]) / (int(foundRankRecord["wins"]) + int(foundRankRecord["losses"]))) }', inline=True)

	return soloRankRecordEmbed



@bot.command(name='rank-solo', help='List stats for solo rank - add username after command.')
async def rank_solo(context, *usernameTokens):
	username, urlFriendlyUsername = api_commons.parse_username_tokens(usernameTokens)


	url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ urlFriendlyUsername }'
	print(f'Using {url} to get summoner ID')

	r = requests.get(url, headers = api_commons.get_headers())

	try:
		response = r.json()
		userId = response['id']

		try:
			print(f'Sending {username} their rank results.')
			await context.send( embed=get_ranked_results(username, userId, 'solo') )
			return
		except Exception:
			print(f'Error retreiving {username} rank results.')
			await context.send(f'{username} does not have Solo/Duo Rank games.')
			return
	except KeyError as exception:
		if r.status_code == 403:
			print('Riot API has expired.')
			await context.send(f'Error connecting to riot servers.')
			return
		elif r.status_code == 404:
			print(f'{username} is not a real user.')
			await context.send(f'{username} is not registered with Riot.')
			return