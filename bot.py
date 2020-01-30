import os
import threading
from multiprocessing import Process

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


def get_ranked_results(username, userId):
	r = requests.get(f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{userId}'
	, headers = get_headers())

	response = r.json()[0]


	hotstreak = ''
	if response['hotStreak'] == True:
		hotstreak = 'You are on fire right now! Keep the win streak up.'

	return f'Solo/Duo Queue Ranked stats for ***{username}***\n**Rank:** {response["tier"]}-{response["rank"]} {response["leaguePoints"]}LP\n**Wins:** {response["wins"]}\n**Losses:** {response["losses"]}\n{hotstreak}'


@bot.command(name='rank-solo', help='List stats for solo rank - add username after command.')
async def rank_solo(context, *usernameTokens):
	username = ''

	for token in usernameTokens:
		username += f'{token} '

	username = username.rstrip()
	urlFriendlyUsername = username.replace(' ', '%20')

	url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ urlFriendlyUsername }'
	print(f'Using {url} to get summoner ID')

	r = requests.get(url, headers = get_headers())

	try:
		response = r.json()
		userId = response['id']

		try:
			print(f'Sending {username} their rank results.')
			await context.send(get_ranked_results(username, userId))
			return
		except IndexError:
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


from flask import Flask
app = Flask(__name__)

@app.route('/testcall')
def test():
	return 'API up and running'


if __name__ == '__main__':

	port = int(os.getenv('PORT', 8081))
	host = '0.0.0.0'

	threading.Thread( target=app.run, args=(), kwargs={'host': host, 'port': port } ).start()

	#p = Process(target=client.run, args=(discordApiToken, ))
	#p.start()
	bot.run(discordApiToken)