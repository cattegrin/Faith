from discord.ext import commands
import re
from faith_utilities import get_rsn
from faith_utilities import get_user

class User:
    def __init__(self, client):
        self.client = client
        self.counter = 0

    @commands.command(name='setrsn',
                      brief='Associates your RSN with your Discord.',
                      pass_context=True)
    async def setrsn(self, context):
        message = context.message.content
        if len(message) < 9:
            await self.client.say("Usage: ::setrsn <name>")
            return
        if '<' in message:
            await self.client.say("Please do not include brackets when setting your RSN. For example, do ::setrsn Faith")
            return

        name = message[9:]  # parses RSN to be set from message
        user = context.message.author.mention  # gets mention of user
        user = re.sub("<|>|!|@", "", user)  # strips extraneous characters from user ID

        if get_user(context, name) is not None:  # if the RSN has been claimed
            await self.client.say("The username " + name + " has been claimed. Please contact an Admin for help.")
        elif get_rsn(user) is not None:  # if the user has claimed a name
            await self.client.say("You have already claimed a name. Please use ::updatersn <name>")
        else:  # user hasn't claimed a name and name is not taken
            aff = open('users.txt', 'a')  # opens user file as append

            combo = user + ":" + name  # stores user ID and RSN combo as string
            aff.write(combo + "\n")  # writes user ID and RSN combo to file
            aff.close()  # closes the user file

            await self.client.say(
                context.message.author.mention + " has claimed the RSN " + name + ".")  # responds to user letting them know their name has been set

        await self.client.send_message(context.message.channel.server.owner,
                                       "User " + context.message.author.mention + " has tried to claim the RSN " + name)


    @commands.command(name='updatersn',
                      brief='Updates your RSN if you have already set one.',
                      pass_context=True)
    async def updatersn(self, context):
        message = context.message.content
        if (len(message) < 13):
            await self.client.say("Usage: ::updatersn <new name>")
            return

        users = open('users.txt', 'r')  # opens user file
        all_users = users.read()  # reads in users
        users.close()  # closes user file

        name = message[12:]  # gets new RSN to be set from message
        pairs = all_users.split("\n")  # splits users into array

        user = context.message.author.mention  # gets user mention of author
        user = re.sub("<|>|!|@", "", user)

        if get_rsn(user) is None:
            await self.client.say("Hey " + context.message.author.mention + ", you haven't set your RSN yet."
                                                                       "You can set it with ::setrsn <name>")
        elif get_user(context, name) is None:  # checks if RSN is taken
            for idx, a in enumerate(pairs):  # runs through user list and modifies appropriate user
                if user in pairs[idx]:
                    pairs[idx] = user + ":" + name

            rewrite_users = open('users.txt', 'w')  # opens user list
            for idx, a in enumerate(pairs):
                rewrite_users.write(pairs[idx] + "\n")  # rewrites user list to file
            rewrite_users.close()  # closes user file
            await self.client.say(
                context.message.author.mention + " has changed their RSN to " + name + ".")  # responds to user to let them know their name has been updated
        elif get_user(context, name) == user:
            await self.client.say("You have already claimed the name " + name + ".")
        elif get_user(context, name) is not None:
            await self.client.say(
                "The username " + name + " has been claimed. Please contact an Admin for help.")  # lets user know requested RSN is claimed.

    @commands.command(name='checkrsn',
                      brief='Check to see what your RSN is set to.',
                      pass_context=True)
    async def checkrsn(self, context):
        player_rsn = get_rsn(context.message.author.mention)  # gets RSN of user

        if player_rsn is None:  # checks if name is not set
            await self.client.say("You have not set your RSN yet " + context.message.author.mention)
        else:  # prints saved RSN
            await self.client.say("Your RSN is set to " + player_rsn + ".")

def setup(client):
    client.add_cog(User(client))