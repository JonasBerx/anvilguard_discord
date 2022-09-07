from ast import alias
from re import U
import discord
import os
import random
from dotenv import load_dotenv
import json
import asyncio

import requests

from discord.ext import commands
from discord.ext.commands import MissingRole, CommandNotFound

# 0. Env setup
load_dotenv()

bot = commands.Bot(command_prefix=';', intents=discord.Intents.all())
token = os.getenv('TOKEN')
rest_api = os.getenv('REST_API')


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# 0.1 Set up item database
with open('./data/item_db.json') as d:
    item_database = {}
    keys_to_retain = ['itemId', 'name', 'class', 'subclass',
                      'quality', 'itemLevel', 'requiredLevel', 'icon']
    item_list = json.load(d)
    i = 0
    for item in item_list:
        i += 1
        item = {your_key: item[your_key] for your_key in keys_to_retain}
        item_database[item['name']] = item


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRole):
        await ctx.send(f"You do **not** have the required role to use this command.")
    if isinstance(error, CommandNotFound):
        await ctx.send(f"{str(error)}")


@bot.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(bot))
    while True:
        statusType = random.randint(0, 1)
        if statusType == 0:
            statusNum = random.randint(0, 10)
            await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name='Everlook WoW'))
        else:
            statusNum = random.randint(0, 10)
            await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name='Gundrik beat up some Trolls'))
        await asyncio.sleep(600)


@bot.command(aliases=['ping', 'latency'])
async def latency_check(ctx):
    res = ""
    embed = discord.Embed(
        title="Latency report",
        description=""
    )
    if round(bot.latency) <= 50:
        embed.description = f'Loremaster is running well: {round(bot.latency, 1)}ms'
    else:
        embed.description = f'Loremaster is having some trouble: {round(bot.latency, 1)}ms'
    await ctx.send(embed=embed)


@bot.command()
async def test(ctx, arg1, arg2):
    await ctx.send(f'You passed {arg1} and {arg2}')


@bot.command()
async def find_all_bounties(ctx):
    url = rest_api+'/bounty'
    x = requests.get(url)
    outp_str = ''

    print(x.json())
    await ctx.send('Retrieving bounties ...')
    i = 0
    for entry in x.json():
        i += 1
        print(entry)
        output = f'{i}. Target: {entry["playerName"]} - Reward: {entry["reward"]}\n'
        outp_str += output
        print(outp_str)
    await ctx.send(outp_str)


@bot.command(aliases=['bounty', 'hunt', 'target'])
async def register_bounty_target(ctx, playername, prize="No reward", player_race="", player_class=""):
    output_string = f'Bounty registered!\nTarget: {playername} | Reward: {prize}'
    if player_race != "":
        output_string += f' | {player_race}'
    if player_class != "":
        output_string += f' | {player_class}'

    # TODO POST request to REST API
    url = rest_api+'/bounty'
    params = {'playerName': f'{playername}',
              'playerRace': f'{player_race}', 'playerClass': f'{player_class}', 'prize': f'{prize}'}

    x = requests.post(url, json=params)

    print(x.status_code)

    if x.status_code == 200:
        await ctx.send(output_string)
    else:
        await ctx.send('Something went wrong, please try again later.')


@bot.command(aliases=['repair', 'r'])
async def send_repair_in(ctx, amount):
    # Bot-testing channel in Anvilguard
    channel = bot.get_channel(1015742051595329717)
    await ctx.send(f'You registered a repair bill for {amount}.\nThe Anvilguard will reimburse you soon.')
    await channel.send(f"<@{ctx.message.author}> requested reimbursement for {amount}")


@bot.command(aliases=['contr', 'c', 'contribute'])
@commands.has_role('Thane')
async def contribute_to_guild_ledger(ctx, item_name, amount):
    author = ctx.message.author
    # TODO Send data to google spreadsheet to track.
    await ctx.reply(f'Registered contribution: **{str(item_name)}** - **{str(amount)} units**!\nThank you <@{str(author.id)}>')


@bot.command(aliases=['gif', 'dwarf'])
async def send_gif(ctx, arg=None):
    if arg == None:
        with open('./flair/gifs/dance.gif', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
    else:
        with open('./flair/gifs/'+str(arg)+'.gif', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)


@bot.command(aliases=['find', 'search', 'item', 'f'])
async def find_item_in_database(ctx, *args):
    _full_name = ' '.join(args)
    req_item = item_database.get(_full_name)

    wowhead_url = 'https://classic.wowhead.com/item=' + str(req_item['itemId'])
    # https://wow.zamimg.com/images/wow/icons/large/
    icon_url = 'https://wow.zamimg.com/images/wow/icons/large/' + \
        req_item['icon'] + '.jpg'
    embed = discord.Embed(
        title=req_item['name'],
        url=wowhead_url,
        description='Item ID: ' + str(req_item['itemId']), color=0x964B00)
    embed.set_thumbnail(url=icon_url)
    embed.add_field(name="Quality", value=str(
        req_item['quality']), inline=True)
    embed.add_field(name="Required Level", value=str(
        req_item['requiredLevel']), inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    embed.add_field(name="Type", value=str(req_item['class']), inline=True)
    embed.add_field(name="Subtype", value=str(
        req_item['subclass']), inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True)

    await ctx.send(embed=embed)


bot.run(token)
