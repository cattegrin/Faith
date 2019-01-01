from discord.ext import commands
from discord.utils import find
from discord.utils import get
from faith_user import get_user
from faith_user import get_rsn
import re
import random
import json
import aiohttp


class General:
    def __init__(self, client):
        self.client = client
        self.counter = 0

    @commands.command(name='8ball',
                      description="Answers a yes/no question.",
                      brief="Answers from the beyond.",
                      aliases=['eight_ball', 'eightball', '8-ball'],
                      pass_context=True)
    async def eight_ball(self, context):
        user = context.message.author.mention  # sets user to the mention of the message author
        user = re.sub("<|>|!|@", "", user)  # removes extraneous characters from user ID

        player_rsn = get_rsn(user)  # gets the rsn of the user
        if player_rsn is None:  # checks if player has not set RSN
            await self.client.say("I noticed you haven't yet set your RSN, you can do so by doing ::setrsn <name>.\n")

        elif player_rsn.lower() == 'malnec' or player_rsn.lower() == 'no wait nvm':  # checks if messenger is Malnec or Ace
            possible_responses = [
                'Fuck yes',
                'Hell no',
                "I don't like you",
                'Can you like, ask someone else',
                'Stop spamming me with questions',
                'I mean kinda yeah',
                'Please DONT do that',
                'Why are you even asking just go p500',
                'Just leave',
                "Hold on I'm at the sand casino",
                '8ball machine broke',
                'Ask Darth',
                'Ask your mother'
            ]
            await self.client.say(random.choice(
                possible_responses) + ", " + context.message.author.mention)  # picks a random option and sends it back to command user
        elif player_rsn is not None:
            possible_responses = [
                'That is a resounding no',
                'It is not looking likely',
                'Too hard to tell',
                'It is quite possible',
                'Definitely',
                'What are you, a cop',
                "I don't feel comfortable answering that",
                'Why are you even asking, its obviously a yes',
                'Just no'
            ]
            await self.client.say(random.choice(
                possible_responses) + ", " + context.message.author.mention)  # picks a random option and sends it back to command user

    @commands.command(name='bitcoin',
                    brief='Finds the price of Bitcoin.')
    async def bitcoin(self):
        url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'  # URL of bitcoin price tool
        async with aiohttp.ClientSession() as session:  # Async HTTP request
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            await self.client.say("Bitcoin price is: $" + response['bpi']['USD']['rate'])

    @commands.command(name='square',
                    brief='Squares a number.')
    async def square(self, number):
        squared_value = int(number) * int(number)  # takes in a value and squares it
        await self.client.say(str(number) + " squared is " + str(squared_value))  # prints result to user

    @commands.command(name='hello',
                      brief='Says hello!',
                      pass_context=True)
    async def hello(self, context):
        player_rsn = get_rsn(context.message.author.mention)  # gets RSN of user
        if player_rsn is None:  # checks if RSN has been set
            await self.client.say("Hello " + context.message.author.mention + "!")  # says hello to user using their mention
        else:
            await self.client.say("Hello " + player_rsn + "!")  # says hello to user using their RSN

    @commands.command(name='ticket',
                      brief='Sends a support ticket to Server Owner.',
                      pass_context=True)
    async def ticket(self, context):
        await self.client.delete_message(context.message)  # removes message from chat in case of sensitive content
        await self.client.send_message(context.message.author,
                                  "Ticket received!")  # messages author letting them know message was received
        await self.client.send_message(context.message.channel.server.owner,
                                  "Ticket from " + context.message.author.mention + ":\n" + context.message.content[
                                                                                            8:])  # sends ticket info to server owner


def setup(client):
    client.add_cog(General(client))
