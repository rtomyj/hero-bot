# bot.py
import os

import discord
from dotenv import load_dotenv
import requests

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = discord.Client()

def get_headers():
	return {
		'Accept-Charset': 'application/x-www-form-urlencoded;charset=UTF-8',
		'X-Riot-Token': os.getenv('RIOT_API_KEY'),
		'Accept-Language': 'en-us'
	}

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')

	for guild in client.guilds:
		print(f'connected to: {guild}')


@client.event
async def on_member_join(member):
	case_insensitive_display_name = member.display_name.lower()

	if case_insensitive_display_name.find('hero') != -1 or case_insensitive_display_name.find('supreme') != -1:
		formality = 'I like your name.'


	await member.create_dm()
	await member.dm_channel.send(f'Hey {member.display_name}! {formality} I am a bot for {member.guild}')


@client.event
async def on_message(message):
	if message.author == client.user:	return

	content = message.content.lower()
	if content.find('ranked stats') != -1:
		r = requests.get('https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/nrxK9HtmDfjyTWQnRryeuWJ5juC_cyUrFN2AER6nwRhUGVA'
		, headers = get_headers())

		response = r.json()[0]

		if response['hotStreak'] == True:
			hotstreak = 'You are on fire right now! Keep the win streak up.'

		await message.channel.send(f'**Rank:** {response["tier"]}-{response["rank"]} {response["leaguePoints"]}LP\n**Wins:** {response["wins"]}\n**Losses:** {response["losses"]}\n{hotstreak}')

client.run(token)
