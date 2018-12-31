'''
IMPORT STATEMENTS
'''
import asyncio
import aiohttp
import json
from discord import Game
from discord.ext.commands import Bot
from discord.utils import get
from discord.utils import find
import re
import random
import time
import schedule
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

'''
GLOBAL VARIABLES
'''
BOT_PREFIX = ("::")
token_file = open('token.txt', 'r')
TOKEN = token_file.read()   #Get at discordapp.com/developers/applications/me
token_file.close()

client = Bot(command_prefix=BOT_PREFIX)

ss_season = False



'''
General Commands
'''


@client.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                pass_context=True)
async def eight_ball(context):
    user = context.message.author.mention   #sets user to the mention of the message author
    user = re.sub("<|>|!|@", "", user)      #removes extraneous characters from user ID

    player_rsn = get_rsn(user)              #gets the rsn of the user
    if player_rsn is None:                  #checks if player has not set RSN
        await client.say("I noticed you haven't yet set your RSN, you can do so by doing ::setrsn <name>.\n")

    elif player_rsn.lower() == 'malnec' or player_rsn.lower() == 'no wait nvm': #checks if messenger is Malnec or Ace
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
        await client.say(random.choice(possible_responses) + ", " + context.message.author.mention) #picks a random option and sends it back to command user
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
        await client.say(random.choice(possible_responses) + ", " + context.message.author.mention) #picks a random option and sends it back to command user


@client.command(name='bitcoin',
                brief='Finds the price of Bitcoin.')
async def bitcoin():
    url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'   #URL of bitcoin price tool
    async with aiohttp.ClientSession() as session:  # Async HTTP request
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        await client.say("Bitcoin price is: $" + response['bpi']['USD']['rate'])


@client.command(name='square',
                brief='Squares a number.')
async def square(number):
    squared_value = int(number) * int(number)   #takes in a value and squares it
    await client.say(str(number) + " squared is " + str(squared_value)) #prints result to user


@client.command(name='hello',
                brief='Says hello!',
                pass_context=True)
async def hello(context):
    player_rsn = get_rsn(context.message.author.mention)    #gets RSN of user
    if player_rsn is None:  #checks if RSN has been set
        await client.say("Hello " + context.message.author.mention + "!")   #says hello to user using their mention
    else:
        await client.say("Hello " + player_rsn + "!")                       #says hello to user using their RSN


'''
RSN: Set, Update, Check, and Utilities
'''


@client.command(name='setrsn',
                brief='Associates your RSN with your Discord.',
                pass_context=True)
async def setrsn(context):
    message = context.message.content
    if len(message) < 10:
        await client.say("Usage: ::updatersn <new name>")
        return

    name = message[9:]      #parses RSN to be set from message
    user = context.message.author.mention   #gets mention of user
    user = re.sub("<|>|!|@", "", user)      #strips extraneous characters from user ID

    if get_user(context, name) is not None:                  #if the RSN has been claimed
        await client.say("The username " + name + " has been claimed. Please contact an Admin for help.")
    elif get_rsn(user) is not None:               #if the user has claimed a name
        await client.say("You have already claimed a name. Please use ::updatersn <name>")
    else:                                   #user hasn't claimed a name and name is not taken
        aff = open('users.txt', 'a')        #opens user file as append

        combo = user + ":" + name           #stores user ID and RSN combo as string
        aff.write(combo + "\n")             #writes user ID and RSN combo to file
        aff.close()                         #closes the user file

        await client.say(context.message.author.mention + " has claimed the RSN " + name + ".")     #responds to user letting them know their name has been set


@client.command(name='updatersn',
                brief='Updates your RSN if you have already set one.',
                pass_context=True)
async def updatersn(context):
    message = context.message.content
    if (len(message) < 13):
        await client.say("Usage: ::updatersn <new name>")
        return

    users = open('users.txt', 'r')          #opens user file
    all_users = users.read()                #reads in users
    users.close()                           #closes user file

    name = message[12:]     #gets new RSN to be set from message
    pairs = all_users.split("\n")           #splits users into array

    user = context.message.author.mention   #gets user mention of author
    user = re.sub("<|>|!|@", "", user)

    if get_rsn(user) is None:
        await client.say("Hey " + context.message.author.mention + ", you haven't set your RSN yet."
                                                                   "You can set it with ::setrsn <name>")
    elif get_user(context, name) is None:        #checks if RSN is taken
        for idx, a in enumerate(pairs):     #runs through user list and modifies appropriate user
            if user in pairs[idx]:
                pairs[idx] = user + ":" + name

        rewrite_users = open('users.txt', 'w')      #opens user list
        for idx, a in enumerate(pairs):
            rewrite_users.write(pairs[idx] + "\n")  #rewrites user list to file
        rewrite_users.close()                       #closes user file
        await client.say(context.message.author.mention + " has changed their RSN to " + name + ".")    #responds to user to let them know their name has been updated
    elif get_user(context, name) == user:
        await client.say("You have already claimed the name " + name + ".")
    elif get_user(context, name) is not None:
        await client.say("The username " + name + " has been claimed. Please contact an Admin for help.")   #lets user know requested RSN is claimed.


@client.command(name='checkrsn',
                brief='Check to see what your RSN is set to.',
                pass_context=True)
async def checkrsn(context):
    player_rsn = get_rsn(context.message.author.mention)    #gets RSN of user

    if player_rsn is None:                                  #checks if name is not set
        await client.say("You have not set your RSN yet " + context.message.author.mention)
    else:                                                   #prints saved RSN
        await client.say("Your RSN is set to " + player_rsn + ".")


def get_rsn(user):                                  #gets the RSN of a user
    users = open('users.txt', 'r')                  #opens user file
    all_users = users.read()                        #reads in user list
    users.close()                                   #closes user file

    user = re.sub("<|>|!|@", "", user)              #removes extraneous characters from user ID

    pairs = all_users.split("\n")                   #splits user list into individual users

    for idx, a in enumerate(pairs):             #loop through list elements
        if user in pairs[idx]:                  #checks if loop has reached correct element
            user_info=pairs[idx].split(':')     #splits element into ID and RSN
            return user_info[1]                 #returns RSN
    return None                                     #returns None if RSN not set


def get_user(context, rsn):                             #gets user mention from RSN
    users = open('users.txt', 'r')                      #opens user list file
    all_users = users.read()                            #reads in user list
    users.close()                                       #closer user list file

    user_list = all_users.split('\n')                   #splits all users into individual user ID:RSN combos

    for u in user_list:                                 #loops through user list
        if rsn in u:                                    #checks if target RSN belongs to current element
            user_split = u.split(':')                   #splits element into ID and RSN
            user_handle = user_split[0]                 #takes user ID from user info
            user_handle = "<@!" + user_handle + ">"     #adds extraneous characters to handle

            user = find(lambda m: m.mention == user_handle, context.message.channel.server.members)         #stores info for me for testing purposes
            if user is None:                                                                                #check if it used the wrong mention
                user_handle = re.sub("!", "", user_handle)                                                  #removes ! from mention
                user = find(lambda m: m.mention == user_handle, context.message.channel.server.members)     #re saves user

            if user is not None:
                return user_handle
            else:
                return None


'''
Server Utilities: Register, Ticket, Get Mention, Bedtime, on_ready, status
'''


@client.command(name='register',
                brief='Gives permissions to new users.',
                pass_context=True)
async def register(context, key):
    if key != 110:                                              #checks to see if key is correct
        await client.say("Incorreect key. Please contact a server member for the key.")
    else:
        client.delete_message(context.message)                  #removes message so key is not made public
        user = context.message.author                           #gets user from message
        verified_role = get(user.server.roles, name='FIH Ally') #gets role to give user
        client.add_role(user, verified_role)                    #adds role to user
        await client.send_message(user, "User verified!")       #sends a message confirming they were verified


@client.command(name='ticket',
                brief='Sends a support ticket to Server Owner.',
                pass_context=True)
async def ticket(context):
    await client.delete_message(context.message)                            #removes message from chat in case of sensitive content
    await client.send_message(context.message.author, "Ticket received!")   #messages author letting them know message was received
    await client.send_message(context.message.channel.server.owner, "Ticket from " + context.message.author.mention + ":\n" + context.message.content[8:])  #sends ticket info to server owner


@client.command(name='get_mention',
                brief='Mentions a user based on their RSN',
                pass_context=True)
async def get_mention(context):
    user_roles = context.message.author.roles       #gets user role list
    for role in user_roles:                         #loops through user roles
        if '🗝️ FiH Leader' == role.name:            #checks if user has role to use command
            name = context.message.content[14:]                                                  #retrieves RSN argument from command
            await client.send_message(context.message.author.mention, '\\' + get_user(name))     #sends mention of requested user
            return


@client.event
async def on_ready():
    print("Logged in as " + client.user.name)   #prints to console that bot has connected
    await client.change_presence(game=Game(name="RuneScape 3 Mobile"))  #sets game being played by bot


async def list_servers():
    await client.wait_until_ready()                         #waits for client to be ready
    while not client.is_closed:                             #checks if client connection is open
        print("Current servers:")                           #prints connected servers list to console
        for server in client.servers:
            print(server.name)

        user_file = open('users.txt', 'r+')                 #opens user file
        user_list = user_file.read()                        #reads in user list

        if ('<' or '>' or '!' or '@') in user_list:         #checks if extraneous symbols exist in user list
            user_file.seek(0)                               #goes to start of file
            user_file.truncate()                            #clears file

            user_list = re.sub("<|>|!|@", "", user_list)    #removes extraneous symbols from user IDs
            user_list = re.sub("\n\n", "\n", user_list)
            user_file.write(user_list)                      #writes fixed list to file

            print("User list cleaned.")

        user_file.close()                                   #closes user file

        await asyncio.sleep(600)                            #5 minute sleep


@client.command(name='bedtime',
                brief='Puts Faith to sleep.',
                pass_context=True)
async def bedtime(context):
    user_roles = context.message.author.roles       #gets user role list
    for role in user_roles:                         #loops through user roles
        if '🗝️ FiH Leader' == role.name:
            sys.exit()


'''
Citadel: Capped, Reset
'''


@client.command(name='capped',
                brief='Reports that you capped at the citadel this week.',
                pass_context=True)
async def capped(context):
    player_rsn=get_rsn(context.message.author.mention)              #gets RSN of player
    if player_rsn is None:                                          #checks to see that RSN has been set
        await client.say("Hey " + context.message.author.mention + ", please set your rsn before using this command. "
                                                                   "You can set it by doing ::setrsn <name>.")
        return                                                      #exits function

    capped = open('capped.txt', 'r')            #opens list of capped users
    capped_list = capped.read()                 #reads in capped users
    capped.close()                              #closes list

    if player_rsn in capped_list:               #checks if player has already capped
        await client.say("Hey " + player_rsn + ", you've already capped this week.")
        return

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

    try:    #creates client and opens rank spreadsheet
        g_client = gspread.authorize(creds)
        sheet = g_client.open("RuneScape Clan Ranks by Points").get_worksheet(1)

        # updates user points
        row = sheet.find(player_rsn).row
        sheet.update_cell(row, 7, int(sheet.cell(row, 7).value) + 5)

        capped_write = open('capped.txt', 'a')  # opens capped list in append mode
        capped_write.write(player_rsn + '\n')  # adds user to list
        capped_write.close()  # closes list

        await client.say("Thanks for capping " + player_rsn + "!")  # thanks the player for capping
    except:
        print("Client operation failed.")

        await client.say("Hey " + get_rsn(context.message.author.mention) + ", there was an error adding your points to the spreadsheet. Please check that the name you set with ::setrsn matches your actual RSN (CaSe SeNSiTiVE")
        return


def citadel_reset():
    capped_list = open('capped.txt', 'r')           #opens capped list
    capped_users = capped_list.read()               #gets users who capped
    capped_list.close()                             #closes list

    clear_capped = open('capped.txt', 'w')      #clears list file
    #write next build tick time
    clear_capped.close()                        #closes list


@client.command(name='citadel_manual_reset',
                brief='Admin command to manually reset capped log.',
                pass_context=True)
async def citadel_manual_reset(context):
    user_roles = context.message.author.roles       #gets user role list
    for role in user_roles:                         #loops through user roles
        if '🗝️ FiH Leader' == role.name:
            capped_list = open('capped.txt', 'r')  # opens capped list
            capped_users = capped_list.read()  # gets users who capped
            capped_list.close()  # closes list

            clear_capped = open('capped.txt', 'w')  # clears list file
            # write next build tick time
            clear_capped.close()  # closes list


'''
Secret Santa: Join and Launch
'''


@client.command(name='launch_santa',
                brief='Gets list of secret santa users.',
                pass_context=True)
async def launch_santa(context):
    """
    Quick note about Discord user mentions before you read this function:
    Discord users all have a unique ID that can be used to mention them as if you were to @ their name.
    I'll call this the user mention. It looks something like this: <@162606971705491458> or <@!179067358369939456>
    Your user mention may or may not have an '!' as it's third character. This is dynamic as far as I know.
    Because of this, user-rsn pairs are saved by the bot based on your ID number, not the extraneous symbols.
    When creating SENDER_LIST, the bot looks up users based on their mention. There is a check in there that removes the
    extra '!' if the user does not have one in their mention
    """

    user_roles = context.message.author.roles       #gets user role list
    for role in user_roles:                         #loops through user roles
        if '🗝️ FiH Leader' == role.name:            #checks if user has role to use command
            santa_file = open('secret_santa.txt', 'r')  #opens secret santa roster
            participants = santa_file.read()            #reads in participant list (set of RSNs)
            santa_file.close()                          #closes secret santa roster

            participant_list = participants.split('\n') #splits participants into list
            participant_users = []                      #creates user array

            for p in participant_list:              #loops through participant list
                user = get_user(p)                  #gets the user associated with given RSN
                if user is not None:                #checks if RSN has been claimed by a user
                    participant_users.append(user)  #adds user to participant list

            JAYCOLE = find(lambda m: m.mention == get_user("Jaycole"), context.message.channel.server.members)  #stores info for me for testing purposes
            if JAYCOLE is None:                     #check if it used the wrong mention
                j_user = get_user("Jaycole")        #gets my user mention again
                j_user = re.sub("!", "", j_user)    #removes ! from mention
                JAYCOLE = find(lambda m: m.mention == j_user, context.message.channel.server.members)   #re-saves me


            SENDER_LIST = []    #initialize sender list, which will be an array of Members

            # Member is a subclass of User, member is a Member
            # participant_users is an array of mentions

            for p in participant_users:                                                             #loop through participants
                member = find(lambda m: m.mention == p, context.message.channel.server.members)     #find the person's User based on their mention
                if member is None:                                                                  #checks if it used the wrong mention
                    p = re.sub("!", "", p)                                                          #removes ! from mention
                    member = find(lambda m: m.mention == p, context.message.channel.server.members) #re checks for User based on new mention
                SENDER_LIST.append(member)                                                          #adds user to sender list

            receivers = participant_list    #stores receivers as a pointer to participant list so I don't have to read in twice.

            f = open("santa_log.txt", "w+") #opens log file

            for user in SENDER_LIST:
                s = random.uniform(0, receivers.__len__())      #gets random value within list bounds
                s = round(s)                                    #rounds random number to a usable index
                receiver = receivers[s - 1]                     #gets receiver at that index

                while receiver == get_rsn(user.mention) and receiver is not None:   #redraws if user gets themself or an error
                    s = random.uniform(0, receivers.__len__())
                    s = round(s)
                    receiver = receivers[s - 1]

                receivers.pop(s - 1)                            #removes receiver from list
                try:                                            #tries to send target to user
                    await client.send_message(user, "Hey " + get_rsn(user.mention) + ", Your secret santa target is " + receiver + "!")
                except:                                         #catches if user private messages are set to private, sends target to me
                    await client.send_message(JAYCOLE, "Hey " + get_rsn(user.mention) + ", your secret santa target is " + receiver + "!")

                #await client.send_message(JAYCOLE, "Hey " + get_rsn(user.mention) + ", your secret santa target is " + receiver + "!") - test line to send all targets to me to test function
                f.write((user.name + " got " + receiver + '\n'))        #writes matches to log

                time.sleep(1)                                           #waits one second to avoid overrunning action limits

            f.close()                                                   #closes santa log
            await client.say("Secret Santa targets have been sent out! Check your inbox for your person!")  #announces that santa targets have been sent.


@client.command(name='santa',
                brief='Adds your name to the secret santa event',
                pass_context=True)
async def santa(context):
    player_rsn = get_rsn(context.message.author.mention)        #gets RSN of command user

    ss_entered = open('secret_santa.txt', 'r')                  #opens secret santa roster
    ss_entries = ss_entered.read()                              #reads roster
    ss_entered.close()                                          #closes roster

    if player_rsn is None:  #if RSN hasn't been set inform user
        await client.say("Hey " + context.message.author.mention + ", you have'nt set your RSN. \n"   
                                                                   "Please set it with ::setrsn <name>.")
        return
    elif player_rsn in ss_entries:    #checks if user is already in secret santa
        await client.say("You've already entered the Secret Santa event " + player_rsn + "!")
        return

    ss_list = open('secret_santa.txt', 'a')                     #opens secret santa roster in append mode
    ss_list.write(player_rsn + "\n")                            #adds new user to roster
    ss_list.close()                                             #closes roster
    await client.say(context.message.author.mention + " has joined the Secret Santa event!")    #informs user that they have registered for Secret Santa


schedule.every().monday.at('00:54').do(citadel_reset)
client.loop.create_task(list_servers())
client.run(TOKEN)
