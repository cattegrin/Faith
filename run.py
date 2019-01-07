from discord.ext.commands import Bot
from discord import Game
import schedule
from faith_citadel import citadel_reset
import re
import asyncio

BOT_PREFIX = ("::")
token_file = open('token.txt', 'r')
TOKEN = token_file.read()   #Get at discordapp.com/developers/applications/me
token_file.close()

client = Bot(command_prefix=BOT_PREFIX)
client.load_extension('faith_admin')
client.load_extension('faith_general')
client.load_extension('faith_user')
client.load_extension('faith_citadel')
client.load_extension('faith_seasonal')
client.load_extension('faith_alog')
client.load_extension('faith_utilities')

@client.event
async def on_ready():
    print("Logged in as " + client.user.name)  # prints to console that bot has connected
    await client.change_presence(game=Game(name="RuneScape 3 Mobile"))  # sets game being played by bot


@client.event
async def on_message(message):
    await client.process_commands(message)


async def list_servers():
    await client.wait_until_ready()  # waits for client to be ready
    while not client.is_closed:  # checks if client connection is open
        print("Current servers:")  # prints connected servers list to console
        for server in client.servers:
            print(server.name)

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

        await asyncio.sleep(600)  # 5 minute sleep


ss_season = False

schedule.every().monday.at('00:54').do(citadel_reset)
client.loop.create_task(list_servers())
client.run(TOKEN)
