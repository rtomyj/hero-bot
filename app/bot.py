import os
import threading
from multiprocessing import Process

from discord import Embed, Colour
from discord.ext import commands
from dotenv import load_dotenv
import requests
from flask import Flask

from league_api_calls import match_info, api_commons, ranked_info

### Setup for annotations and env vars ###
load_dotenv()
discordApiToken = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
app = Flask(__name__)



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



@bot.command(name='last-match-stats', help='Displays info about your last game.')
async def get_last_match_stats(context, *usernameTokens):
	global championData
	username, urlFriendlyUsername = api_commons.parse_username_tokens(usernameTokens)
	summonerId = ''

	url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ urlFriendlyUsername }'
	print(f'Using {url} to get summoner ID')

	r = requests.get(url, headers = api_commons.get_headers())

	try:
		response = r.json()
		summonerId = response['id']
	except:
		print('Error fetching username')

	gameId = match_info.get_most_recent_game_id(username, urlFriendlyUsername)
	riotMatchData = match_info.get_match_data_by_game_id(gameId)
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



@app.route('/testcall')
def test():
	return 'API up and running'



### Main code segment ###
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