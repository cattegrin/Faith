from discord.ext.commands import Bot
from discord import Game
import schedule
from faith_citadel import citadel_reset
from faith_alog import update_logs
from faith_rsNewsfeed import check_news_feed
import re
import asyncio
import discord
import time

BOT_PREFIX = ("::")
token_file = open('token.txt', 'r')
TOKEN = token_file.read()   #Get at discordapp.com/developers/applications/me
token_file.close()

client = Bot(command_prefix=BOT_PREFIX)
client.load_extension('faith_admin')
client.load_extension('faith_alog')
client.load_extension('faith_general')
client.load_extension('faith_user')
client.load_extension('faith_citadel')
client.load_extension('faith_seasonal')
client.load_extension('faith_rsAPI')
client.load_extension('faith_rsNewsfeed')

@client.event
async def on_ready():
    print("Logged in as " + client.user.name)  # prints to console that bot has connected
    await client.change_presence(activity=discord.Game(name='Game of Thrones but PC'))
    client.loop.create_task(list_servers())
    client.loop.create_task(update_logs())
    client.loop.create_task(check_news_feed(client))


@client.event
async def on_message(message):
    await client.process_commands(message)



async def list_servers():
    await client.wait_until_ready()  # waits for client to be ready
    while not client.is_closed():  # checks if client connection is open
        print("Current servers:")  # prints connected servers list to console
        for guild in client.guilds:
            print(guild.name)

        user_file = open('users.txt', 'r+')  # opens user file
        user_list = user_file.read()  # reads in user list

        if ('<' or '>' or '!' or '@') in user_list:  # checks if extraneous symbols exist in user list
            user_file.seek(0)  # goes to start of file
            user_file.truncate()  # clears file
            user_list = re.sub("<|>|!|@", "", user_list)  # removes extraneous symbols from user IDs
            user_list = re.sub("\n\n", "\n", user_list)
            user_file.write(user_list)  # writes fixed list to file

            print("User list cleaned.")

        user_file.close()  # closes user file
        update_logs()

        await asyncio.sleep(600)  # 5 minute sleep


ss_season = False

schedule.every().monday.at('00:54').do(citadel_reset)

time.sleep(5)

client.run(TOKEN)

