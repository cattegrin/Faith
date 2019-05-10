from discord.ext import commands
from discord.utils import find
from discord.utils import get
from faith_utilities import get_user
from faith_utilities import get_rsn
import random
import time
import re

ss_season = False

class Seasonal(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.counter = 0


    '''
    Secret Santa: Join and Launch
    '''

    @commands.command(name='launch_santa',
                      brief='Gets list of secret santa users.',
                      pass_context=True)
    async def launch_santa(self, context):
        """
        Quick note about Discord user mentions before you read this function:
        Discord users all have a unique ID that can be used to mention them as if you were to @ their name.
        I'll call this the user mention. It looks something like this: <@162606971705491458> or <@!179067358369939456>
        Your user mention may or may not have an '!' as it's third character. This is dynamic as far as I know.
        Because of this, user-rsn pairs are saved by the bot based on your ID number, not the extraneous symbols.
        When creating SENDER_LIST, the bot looks up users based on their mention. There is a check in there that removes the
        extra '!' if the user does not have one in their mention
        """

        user_roles = context.message.author.roles  # gets user role list
        for role in user_roles:  # loops through user roles
            if '🗝️ FiH Leader' == role.name:  # checks if user has role to use command
                santa_file = open('secret_santa.txt', 'r')  # opens secret santa roster
                participants = santa_file.read()  # reads in participant list (set of RSNs)
                santa_file.close()  # closes secret santa roster

                participant_list = participants.split('\n')  # splits participants into list
                participant_users = []  # creates user array

                for p in participant_list:  # loops through participant list
                    user = get_user(p)  # gets the user associated with given RSN
                    if user is not None:  # checks if RSN has been claimed by a user
                        participant_users.append(user)  # adds user to participant list

                JAYCOLE = find(lambda m: m.mention == get_user("Jaycole"),
                               context.message.channel.server.members)  # stores info for me for testing purposes
                if JAYCOLE is None:  # check if it used the wrong mention
                    j_user = get_user("Jaycole")  # gets my user mention again
                    j_user = re.sub("!", "", j_user)  # removes ! from mention
                    JAYCOLE = find(lambda m: m.mention == j_user, context.message.channel.server.members)  # re-saves me

                SENDER_LIST = []  # initialize sender list, which will be an array of Members

                # Member is a subclass of User, member is a Member
                # participant_users is an array of mentions

                for p in participant_users:  # loop through participants
                    member = find(lambda m: m.mention == p,
                                  context.message.channel.server.members)  # find the person's User based on their mention
                    if member is None:  # checks if it used the wrong mention
                        p = re.sub("!", "", p)  # removes ! from mention
                        member = find(lambda m: m.mention == p,
                                      context.message.channel.server.members)  # re checks for User based on new mention
                    SENDER_LIST.append(member)  # adds user to sender list

                receivers = participant_list  # stores receivers as a pointer to participant list so I don't have to read in twice.

                f = open("santa_log.txt", "w+")  # opens log file

                for user in SENDER_LIST:
                    s = random.uniform(0, receivers.__len__())  # gets random value within list bounds
                    s = round(s)  # rounds random number to a usable index
                    receiver = receivers[s - 1]  # gets receiver at that index

                    while receiver == get_rsn(
                            user.mention) and receiver is not None:  # redraws if user gets themself or an error
                        s = random.uniform(0, receivers.__len__())
                        s = round(s)
                        receiver = receivers[s - 1]

                    receivers.pop(s - 1)  # removes receiver from list
                    try:  # tries to send target to user
                        await self.client.send_message(user, "Hey " + get_rsn(
                            user.mention) + ", Your secret santa target is " + receiver + "!")
                    except:  # catches if user private messages are set to private, sends target to me
                        await self.client.send_message(JAYCOLE, "Hey " + get_rsn(
                            user.mention) + ", your secret santa target is " + receiver + "!")

                    # await client.send_message(JAYCOLE, "Hey " + get_rsn(user.mention) + ", your secret santa target is " + receiver + "!") - test line to send all targets to me to test function
                    f.write((user.name + " got " + receiver + '\n'))  # writes matches to log

                    time.sleep(1)  # waits one second to avoid overrunning action limits

                f.close()  # closes santa log
                await context.message.channel.send(
                    "Secret Santa targets have been sent out! Check your inbox for your person!")  # announces that santa targets have been sent.

    @commands.command(name='santa',
                    brief='Adds your name to the secret santa event',
                    pass_context=True)
    async def santa(self, context):
        if not ss_season:
            await context.message.channel.send("Hey " + get_rsn(context.message.author.mention) + ", it's not the season for that event!")

        player_rsn = get_rsn(context.message.author.mention)  # gets RSN of command user

        ss_entered = open('secret_santa.txt', 'r')  # opens secret santa roster
        ss_entries = ss_entered.read()  # reads roster
        ss_entered.close()  # closes roster

        if player_rsn is None:  # if RSN hasn't been set inform user
            await context.message.channel.send("Hey " + context.message.author.mention + ", you have'nt set your RSN. \n"
                                                                       "Please set it with ::setrsn <name>.")
            return
        elif player_rsn in ss_entries:  # checks if user is already in secret santa
            await context.message.channel.send("You've already entered the Secret Santa event " + player_rsn + "!")
            return

        ss_list = open('secret_santa.txt', 'a')  # opens secret santa roster in append mode
        ss_list.write(player_rsn + "\n")  # adds new user to roster
        ss_list.close()  # closes roster
        await context.message.channel.send(
            context.message.author.mention + " has joined the Secret Santa event!")  # informs user that they have registered for Secret Santa


def setup(client):
    client.add_cog(Seasonal(client))