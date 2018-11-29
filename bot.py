# Work with Python 3.6
import random
import asyncio
import aiohttp
import json
from discord import Game
from discord.ext.commands import Bot
from discord.utils import get
import datetime
import re

BOT_PREFIX = ("::")
TOKEN = "NTE1MjYwMTQwNTY4NzA3MTA5.Dt3W_g.mqyeKcMKasaoxYmZu0_9YbM-3kE"  # Get at discordapp.com/developers/applications/me

client = Bot(command_prefix=BOT_PREFIX)
ss_season = True


@client.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                pass_context=True)
async def eight_ball(context):
    possible_responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell',
        'It is quite possible',
        'Definitely',
    ]
    await client.say(random.choice(possible_responses) + ", " + context.message.author.mention)


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="Mein Craft"))
    print("Logged in as " + client.user.name)


@client.command(name='bitcoin',
                brief='Finds the price of Bitcoin.')
async def bitcoin():
    url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
    async with aiohttp.ClientSession() as session:  # Async HTTP request
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        await client.say("Bitcoin price is: $" + response['bpi']['USD']['rate'])


@client.command(name='square',
                brief='Squares a number.')
async def square(number):
    squared_value = int(number) * int(number)
    await client.say(str(number) + " squared is " + str(squared_value))


@client.command(name='setrsn',
                brief='Associates your RSN with your Discord.',
                pass_context=True)
async def setrsn(context):
    users = open('users.txt', 'r')
    pairs = users.read()
    users.close()

    name = context.message.content[9:]
    user = context.message.author.mention
    user = re.sub("<|>|!|@", "", user)

    rsn_available = check_rsn(pairs, name)
    user_available = check_user(pairs, user)

    if rsn_available == 1:
        await client.say("The username " + name + " has been claimed. Please contact an Admin for help.")
    if user_available == 1:
        await client.say("You have already claimed a name. Please use ::updatersn <name>")

    if rsn_available == user_available == 0:
        aff = open('users.txt', 'a')

        combo = context.message.author.mention + ":" + name
        aff.write(combo + "\n")
        print(combo)

        aff.close()
        await client.say(context.message.author.mention + " has claimed the RSN " + name + ".")


@client.command(name='updatersn',
                brief='Updates your RSN if you have already set one.',
                pass_context=True)
async def updatersn(context):
    users = open('users.txt', 'r')
    all_users = users.read()
    users.close()
    name = context.message.content[12:]
    pairs = all_users.split("\n")

    user = context.message.author.mention
    user = re.sub("<|>|!|@", "", user)

    if(check_rsn(pairs, name) == 0):
        for idx, a in enumerate(pairs):
            if user in pairs[idx]:
                pairs[idx] = user + ":" + name

        rewrite_users = open('users.txt', 'w')
        for idx, a in enumerate(pairs):
            rewrite_users.write(pairs[idx] + "\n")
        rewrite_users.close()
        await client.say(user + " has changed their RSN to " + name + ".")
    else:
        await client.say("The username " + name + " has been claimed. Please contact an Admin for help.")


@client.command(name='ticket',
                brief='Sends a support ticket to Server Owner.',
                pass_context=True)
async def ticket(context):
    await client.delete_message(context.message)
    await client.send_message(context.message.author, "Ticket received!")
    await client.send_message(context.message.channel.server.owner, "Ticket from " + context.message.author.mention + ":\n" + context.message.content[8:])


@client.command(name='register',
                brief='Gives permissions to new users.',
                pass_context=True)
async def register(context, key):
    if key != 110:
        await client.say("Incorreect key. Please contact a server member for the key.")
    else:
        client.delete_message(context.message)
        user = context.message.author
        verified_role = get(user.server.roles, name='Verified (RuneScape)')
        client.add_role(user, verified_role)
        await client.say("User verified!")



@client.command(name='capped',
                brief='Reports that you capped at the citadel this week.',
                pass_context=True)
async def capped(context):
    player_rsn=get_rsn(context.message.author.mention)
    if player_rsn is None:
        await client.say("Hey " + context.message.author.mention + ", please set your rsn before using this command. You can set it by doing ::setrsn <name>.")

    capped = open('capped.txt', 'r')
    capped_list = capped.read()
    capped.close()

    if player_rsn in capped_list:
        await client.say("Hey " + player_rsn + ", you've already capped this week.")
        return

    capped_write = open('capped.txt', 'a')
    capped_write.write(player_rsn + '\n')
    capped_write.close()

    await client.say("Thanks for capping " + player_rsn + "!")


@client.command(name='citadel_reset',
                brief='Tells the bot that the citadel has reset. Prints users that capped last week.',
                pass_context=True)
async def citadel_reset(context):
    user_roles = context.message.author.roles
    for role in user_roles:
        if '🗝️ FiH Leader' == role.name or '💙 I Fucking Love Cyan' == role.name:
            capped_list = open('capped.txt', 'r')
            capped_users = capped_list.read()
            capped_list.close()

            await client.say("Users that capped this week:\n" + capped_users)

            clear_capped = open('capped.txt', 'w')
            clear_capped.close()
            return

    await client.say("You do not have permission to use this command.")

'''
@client.command(name='resync_users')
async def resync_users():
    user_file = open('users.txt', 'r')
    user_list = user_file.read()
    user_file.close()

    users = user_list.split('\n')
    rewrite_users = open('users.txt', 'w')


    for user in users:
        user = re.sub("<|>|!|@", "", user)
        rewrite_users.write(user + '\n')
'''




@client.command(name='hello',
                brief='Says hello!',
                pass_context=True)
async def hello(context):
    player_rsn = get_rsn(context.message.author.mention)
    if player_rsn is None:
        await client.say("Hello " + context.message.author.mention + "!")
    else:
        await client.say("Hello " + player_rsn + "!")


@client.command(name='santa',
                brief='Adds your name to the secret santa event',
                pass_context=True)
async def santa(context):
    player_rsn = get_rsn(context.message.author.mention)

    ss_entered = open('secret_santa.txt', 'r')
    ss_entries = ss_entered.read()
    ss_entered.close()

    print(player_rsn)

    if player_rsn is None:
        await client.say("Hey " + context.message.author.mention + ", you have'nt set your RSN. \n"   
                                                                   "Please set it with ::setrsn <name>.")
    else:
        if player_rsn in ss_entries:
            await client.say("You've already entered the Secret Santa event " + context.message.author.mention + "!")
            return
        ss_list = open('secret_santa.txt', 'a')
        ss_list.write(player_rsn + "\n")
        ss_list.close()
        await client.say(context.message.author.mention + " has joined the Secret Santa event!")





async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


def check_rsn(pairs, name):
    if name in pairs:
        return 1
    return 0


def check_user(pairs, user):
    if user in pairs:
        return 1
    return 0

def get_rsn(user):
    users = open('users.txt', 'r')
    all_users = users.read()
    users.close()

    pairs = all_users.split("\n")

    if check_user(pairs, user) == 0:
        for idx, a in enumerate(pairs):
            if user in pairs[idx]:
                user_info=pairs[idx].split(':')
                return user_info[1]
    return None

client.loop.create_task(list_servers())
client.run(TOKEN)