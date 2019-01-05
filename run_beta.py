from discord.ext.commands import Bot
from discord import Game
import discord.ext.commands.errors
import schedule
from faith_alog import update_logs
import re
import asyncio

BOT_PREFIX = ("::")
TEST_FUNCTION = ('faith_alog')

token_file = open('token.txt', 'r')
TOKEN = token_file.read()   #Get at discordapp.com/developers/applications/me
token_file.close()


client = Bot(command_prefix=BOT_PREFIX)
client.load_extension('faith_utilities')
client.load_extension(TEST_FUNCTION)



@client.event
async def on_ready():
    print("Logged in as " + client.user.name)  # prints to console that bot has connected
    await client.change_presence(game=Game(name="RuneScape 3 Mobile"))  # sets game being played by bot


@client.event
async def on_message(message):
    try:
        await client.process_commands(message)
    except discord.ext.commands.errors.CommandNotFound:
        print("Command not included in Beta submitted, ignoring...")


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

        update_logs()

        await asyncio.sleep(600)  #10 minute sleep


client.loop.create_task(list_servers())
client.run(TOKEN)
