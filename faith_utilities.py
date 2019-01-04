import re
from discord.utils import find
import os
import sys

class Utilities:
    def __init__(self, client):
        self.client = client
        self.counter = 0


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

def tail(fname, lines):
    bufsize = 8192
    fsize = os.stat(fname).st_size
    iter = 0

    recent_events = []

    with open(fname) as f:
        if bufsize > fsize:
            bufsize = fsize - 1
            data = []
            while True:
                iter += 1
                f.seek(fsize - bufsize * iter)
                data.extend(f.readlines())
                if len(data) >= lines or f.tell() == 0:
                    recent_events.append(''.join(data[-lines:]))
                    break
    return recent_events

def say(client, message):
    client.say(message)


def setup(client):
    client.add_cog(Utilities(client))