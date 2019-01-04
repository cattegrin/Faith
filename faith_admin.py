from discord.ext import commands
from discord.utils import get
from faith_utilities import get_user
import sys


class Admin:
    def __init__(self, client):
        self.client = client
        self.counter = 0


    @commands.command(name='register',
                      brief='Gives permissions to new users.',
                      pass_context=True)
    async def register(self, context, key):
        if key != 110:  # checks to see if key is correct
            await self.client.say("Incorreect key. Please contact a server member for the key.")
        else:
            self.client.delete_message(context.message)  # removes message so key is not made public
            user = context.message.author  # gets user from message
            verified_role = get(user.server.roles, name='FIH Ally')  # gets role to give user
            self.client.add_role(user, verified_role)  # adds role to user
            await self.client.send_message(user, "User verified!")  # sends a message confirming they were verified


    @commands.command(name='get_mention',
                      brief='Mentions a user based on their RSN',
                      pass_context=True)
    async def get_mention(self, context):
        user_roles = context.message.author.roles  # gets user role list
        for role in user_roles:  # loops through user roles
            if '🗝️ FiH Leader' == role.name:  # checks if user has role to use command
                name = context.message.content[14:]  # retrieves RSN argument from command
                await self.client.send_message(context.message.author.mention,
                                          '\\' + get_user(name))  # sends mention of requested user
                return


    @commands.command(name='bedtime',
                      brief='Puts Faith to sleep.',
                      pass_context=True)
    async def bedtime(self, context):
        user_roles = context.message.author.roles  # gets user role list
        for role in user_roles:  # loops through user roles
            if '🗝️ FiH Leader' == role.name:
                sys.exit()


def setup(client):
    client.add_cog(Admin(client))
