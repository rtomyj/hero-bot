import os
import threading
from multiprocessing import Process

from discord import Embed, Colour
from discord.ext import commands
from dotenv import load_dotenv
import requests

load_dotenv()
discordApiToken = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

def get_headers():
	return {
		'Accept-Charset': 'application/x-www-form-urlencoded;charset=UTF-8',
		'X-Riot-Token': os.getenv('RIOT_API_KEY'),
		'Accept-Language': 'en-us'
	}

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord API!')

	for guild in bot.guilds:
		print(f'connected to: {guild}')


@bot.event
async def on_member_join(member):
	case_insensitive_display_name = member.display_name.lower()

	if case_insensitive_display_name.find('hero') != -1 or case_insensitive_display_name.find('supreme') != -1:
		formality = 'I like your name.'


	await member.create_dm()
	await member.dm_channel.send(f'Hey {member.display_name}! {formality} I am a bot for {member.guild}')


def get_ranked_results(username, userId, request):
	REQUEST_maps_QUEUE_TYPE = {'solo': 'RANKED_SOLO_5x5', 'flex': 'RANKED_FLEX_SR'}

	r = requests.get(f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{userId}'
	, headers = get_headers())



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


def parse_username_tokens(usernameTokens):
	username = ''

	for token in usernameTokens:
		username += f'{token} '

	username = username.rstrip()
	urlFriendlyUsername = username.replace(' ', '%20')
	return username, urlFriendlyUsername


@bot.command(name='rank-solo', help='List stats for solo rank - add username after command.')
async def rank_solo(context, *usernameTokens):
	username, urlFriendlyUsername = parse_username_tokens(usernameTokens)


	url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ urlFriendlyUsername }'
	print(f'Using {url} to get summoner ID')

	r = requests.get(url, headers = get_headers())

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


@bot.command(name='last-match-stats', help='Displays info about your last game.')
async def get_last_match_stats(context, *usernameTokens):
	global championData
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
	embedMatchData['championId'] = str( participantData['championId'] )
	embedMatchData['kills'] = participantStats['kills']
	embedMatchData['deaths'] = participantStats['deaths']
	embedMatchData['assists'] = participantStats['assists']


	matchMessage = Embed(color=Colour.from_rgb(224, 17, 95), title=f'Last Match For { embedMatchData["summonerName"] }')
	matchMessage.set_thumbnail(url=f'http://ddragon.leagueoflegends.com/cdn/10.3.1/img/champion/{ championData[embedMatchData["championId"]]["championName"] }.png')
	matchMessage.add_field(name='Team', value=embedMatchData['team'], inline=False)
	matchMessage.add_field(name='Score', value=f'{ embedMatchData["kills"] }/{ embedMatchData["deaths"] }/{ embedMatchData["assists"] }', inline=True)
	matchMessage.add_field(name='KDA', value=float( int(embedMatchData["kills"]) / int(embedMatchData["deaths"]) ))

	await context.send(embed=matchMessage)


from flask import Flask
app = Flask(__name__)

@app.route('/testcall')
def test():
	return 'API up and running'


if __name__ == '__main__':
	port = int(os.getenv('PORT', 8081))
	host = '0.0.0.0'

	threading.Thread( target=app.run, args=(), kwargs={'host': host, 'port': port } ).start()

	global championData
	championData = dict()

	try:
		url = 'http://ddragon.leagueoflegends.com/cdn/10.3.1/data/en_US/champion.json'
		r = requests.get(url)

		riotChampData = r.json()['data']

		for name, data in riotChampData.items():
			championData[ data['key'] ] = {'championName': name}

	except Exception as e:
		print(e)
		print('Err connecting to Riot champion data endpoint')


	bot.run(discordApiToken)