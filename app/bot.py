import asyncio
import os
import threading

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
import requests
from flask import Flask

from cogs.ranked_info import RankedInfo
from cogs.match_info import MatchInfo

import nest_asyncio
nest_asyncio.apply()

### Setup for annotations and env vars ###
load_dotenv()
discordApiToken = os.getenv('DISCORD_TOKEN')

app = Flask(__name__)

intents = Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


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


@bot.command(name="dance")
async def dance(ctx):
    await ctx.send("I don't like to dance :(")


@app.route('/testcall')
def test():
    print("health requested")
    return 'API up and running'


async def setup_bot():
    champion_data = dict()

    try:
        url = 'https://ddragon.leagueoflegends.com/cdn/12.15.1/data/en_US/champion.json'
        r = requests.get(url)

        riot_champ_data = r.json()['data']

        for name, data in riot_champ_data.items():
            champion_data[int(data['key'])] = {'name': name}

    except Exception as e:
        print(e)
        print('Err connecting to Riot champion data endpoint')

    await bot.add_cog(RankedInfo(bot))
    await bot.add_cog(MatchInfo(bot, champion_data))
    bot.run(discordApiToken)


### Main code segment ###
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8004))
    host = '0.0.0.0'

    threading.Thread(target=app.run, args=(), kwargs={'host': host, 'port': port}).start()
    asyncio.get_event_loop().run_until_complete(setup_bot())

