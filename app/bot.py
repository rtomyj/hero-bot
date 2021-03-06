import os
import threading
from multiprocessing import Process

from discord import Embed, Colour
from discord.ext import commands
from dotenv import load_dotenv
import requests
from flask import Flask

from helper import api_commons
from cogs.ranked_info import RankedInfo
from cogs.match_info import MatchInfo

### Setup for annotations and env vars ###
load_dotenv()
discordApiToken = os.getenv('DISCORD_TOKEN')

app = Flask(__name__)
bot = commands.Bot(command_prefix='!')


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


@app.route('/testcall')
def test():
	return 'API up and running'


### Main code segment ###
if __name__ == '__main__':
	port = int(os.getenv('PORT', 8081))
	host = '0.0.0.0'

	threading.Thread( target=app.run, args=(), kwargs={'host': host, 'port': port } ).start()

	championData = dict()


	try:
		url = 'http://ddragon.leagueoflegends.com/cdn/10.3.1/data/en_US/champion.json'
		r = requests.get(url)

		riotChampData = r.json()['data']

		for name, data in riotChampData.items():
			championData[ int(data['key']) ] = {'name': name}

	except Exception as e:
		print(e)
		print('Err connecting to Riot champion data endpoint')

	bot.add_cog( RankedInfo(bot) )
	bot.add_cog( MatchInfo(championData) )
	bot.run(discordApiToken)