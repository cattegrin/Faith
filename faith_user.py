from discord.ext import commands
import re
from discord.utils import find
from discord.utils import get

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


def get_rsn(user):  # gets the RSN of a user
    users = open('users.txt', 'r')  # opens user file
    all_users = users.read()  # reads in user list
    users.close()  # closes user file

    user = re.sub("<|>|!|@", "", user)  # removes extraneous characters from user ID

    pairs = all_users.split("\n")  # splits user list into individual users

    for idx, a in enumerate(pairs):  # loop through list elements
        if user in pairs[idx]:  # checks if loop has reached correct element
            user_info = pairs[idx].split(':')  # splits element into ID and RSN
            return user_info[1]  # returns RSN
    return None  # returns None if RSN not set


def get_user(context, rsn):  # gets user mention from RSN
    users = open('users.txt', 'r')  # opens user list file
    all_users = users.read()  # reads in user list
    users.close()  # closer user list file

    user_list = all_users.split('\n')  # splits all users into individual user ID:RSN combos

    for u in user_list:  # loops through user list
        if rsn in u:  # checks if target RSN belongs to current element
            user_split = u.split(':')  # splits element into ID and RSN
            user_handle = user_split[0]  # takes user ID from user info
            user_handle = "<@!" + user_handle + ">"  # adds extraneous characters to handle

            user = find(lambda m: m.mention == user_handle,
                            context.message.channel.server.members)  # stores info for me for testing purposes
            if user is None:  # check if it used the wrong mention
                user_handle = re.sub("!", "", user_handle)  # removes ! from mention
                user = find(lambda m: m.mention == user_handle,
                            context.message.channel.server.members)  # re saves user

            if user is not None:
                return user_handle
            else:
                return None


def setup(client):
    client.add_cog(User(client))
