import urllib
import os
import sys
import datetime
import xmltodict

from faith_utilities import get_rsn
from faith_utilities import say
from faith_utilities import tail
from discord.ext import commands


class Alog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.counter = 0

    @commands.command(name='alog',
                    brief="Adventurer's Log related commands",
                    pass_context=True)
    async def alog(self, context):
        argv = context.message.content[7:]
        if len(argv) < 2:
            alog_docs = open("alog_docs.txt", 'r')
            alog_help = alog_docs.read()
            alog_docs.close()
            await context.message.channel.send(alog_help)
            return

        args = argv.split(' ')
        rsn = get_rsn(context.message.author.mention)

        if rsn is None:
            await context.message.channel.send("Hey " + context.message.author.mention + ", you haven't set your RSN yet. Set it with ::setrsn")
            return

        if args[0] == 'activate':
            user_tracking = active_tracking(rsn)
            if user_tracking is True:
                await context.message.channel.send("User " + rsn + " added to active tracking roster.")
            else:
                await context.message.channel.send("I'm already keeping track of your adventurer log " + rsn)
        elif args[0] == 'track':
            track(self.client, rsn)
            await context.message.channel.send("User " + rsn + "'s Adventurer Log has been updated.")
        elif args[0] == 'drops':
            await context.message.channel.send("Getting drops for " + rsn)
            await context.message.channel.send(pull_drops(rsn))
        elif args[0] == 'help':
            alog_docs = open("alog_docs.txt", 'r')
            alog_help = alog_docs.read()
            alog_docs.close()
            await context.message.channel.send(alog_help)
            return
        elif args[0] == 'reset':
            await context.message.channel.send("Resetting logs for " + rsn)
            reset_user(rsn)
        else:
            await context.message.channel.send("Command not recognized.")


def track(client, rsn):
    print("Track request received")
    tracking_roster = open(os.path.join(sys.path[0], "alogs/roster.txt"), "r")
    roster = tracking_roster.read()
    print("Roster Saved")
    tracking_roster.close()

    if rsn in roster:
        track_user(rsn)
        say(client, "User " + rsn + "'s Adventurer Log has been updated.")
        print("User " + rsn + "'s Adventurer Log has been updated.")
    else:
        say(client, "Your adventures are not currently being tracked. Please enable tracking by doing ::alog activate")
        print("Your adventures are not currently being tracked. Please enable tracking by doing ::alog activate")


def pull_drops(rsn):
    drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "r")
    drops = drop_log.read()
    return("```------Drop List for " + rsn + '------\n' + drops + "---------------------------------```")


def active_tracking(rsn):
    tracking_roster = open(os.path.join(sys.path[0], "alogs/roster.txt"), "r")
    roster = tracking_roster.read()
    tracking_roster.close()

    if rsn not in roster:
        tracking_roster = open(os.path.join(sys.path[0], "alogs/roster.txt"), "a")
        tracking_roster.write(rsn + '\n')
        tracking_roster.close()

        try:
            os.mkdir("alogs/" + rsn + "/")
            adv_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "adv_log" + ".txt"), "w")
            drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "w")
            xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "w")
            xp_log.write("Experience milestones:0")

            adv_log.close()
            drop_log.close()
            xp_log.close()
        except (FileExistsError):
            print("User files exist, running trace.")

        track_user(rsn)

        LOGGING_FILE = open("alog_beta_log.txt", 'a')
        LOGGING_FILE.write('--------------------------------------------------------------------------\n'
                           'END OF LOG UPDATES\n'
                           '--------------------------------------------------------------------------\n')
        LOGGING_FILE.close()

        return True
    else:
        return False


def track_user(rsn):
        LOGGING_FILE = open("alog_beta_log.txt", 'a')

        LOGGING_FILE.write("-----------------------------------------------------------\n")
        LOGGING_FILE.write("User Being Tracked: " + rsn + "\n")
        LOGGING_FILE.write(datetime.datetime.now().__str__() + "\n")

        rsn_append = ''
        rsn_split = []

        if ' ' in rsn:
            rsn_split = rsn.split(" ")

            for substr in rsn_split:
                rsn_append += substr + '%20'
            rsn_append = rsn_append[:-3]
        else:
            rsn_append = rsn

        user_page = 'http://services.runescape.com/m=adventurers-log/c=tB0ermS1flc/rssfeed?searchName=' + rsn_append
        LOGGING_FILE.write("User URL: " + user_page + '\n')

        try:
            rss_feed = urllib.request.urlopen(user_page)
            data = rss_feed.read()
            rss_feed.close()

            data = xmltodict.parse(data)

            data_table = data['rss']['channel']

            events = data_table['item']
        except urllib.error.HTTPError:
            LOGGING_FILE.write("ERROR: HTTP Error: User page not found.\n")
            LOGGING_FILE.write("RSN: " + rsn + "\n")
            LOGGING_FILE.write("RSN Split: " + str(rsn_split) + '\n')
            LOGGING_FILE.write("RSN Append: " + rsn_append + '\n')
            LOGGING_FILE.write("-----------------------------------------------------------\n\n\n")
            return


        try:
            user_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "adv_log" + ".txt"), "a")
            drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "r+")
            xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "r+")
            check_user_file = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "adv_log" + ".txt"), "r")
        except FileNotFoundError:
            try:
                user_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "adv_log" + ".txt"), "a")
                drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "r+")
                xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "r+")
                check_user_file = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "adv_log" + ".txt"), "r")
            except OSError:
                LOGGING_FILE.write("Creation of the directory failed\n")
                LOGGING_FILE.write("-----------------------------------------------------------\n\n\n")
                return

        try:
            drop_list = drop_log.read()
            drops = drop_list.split('\n')
            drop_log.close()

            xp_info = xp_log.read()
            xp_log.close()
        except NameError:
            LOGGING_FILE.write("Name Error")
            LOGGING_FILE.write("-----------------------------------------------------------\n\n\n")
            return

        # checks if user has stored alog
        if check_user_file.readline().__len__() > 2:
            recent_items = tail("alogs/" + rsn + "/" + "adv_log" + ".txt", 20)

            if recent_items[0] == None:
                LOGGING_FILE.write("SEEK ERROR: Caused during tail of " + rsn +"'s log.")
                return


            re = recent_items[0]
            re_list = re.split('\n')

            reprint_drops = False
            for idx, a in enumerate(events):
                event = events[idx]
                new_event = event['title'] + ": " + event['description']

                if new_event in re_list:
                    remaining_events = events[idx:]
                    utd = True
                    for e in remaining_events:
                        if e not in re_list:
                            utd = False
                    if utd:
                        return
                else:
                    user_log.write(new_event + '\n')

                    if 'I found' in event['title']:
                        if 'a pair of' in event['title']:
                            title = event['title'].split(' ', 5)
                            drop = title[5]
                            drop = drop.strip('.')
                        else:
                            title = event['title']
                            title = title.split(' ', 3)
                            drop = title[3]
                            drop = drop.strip(".")

                        reprint_drops = True

                        existing_drop = False
                        for loc, x in enumerate(drops):
                            LOGGING_FILE.write("Drop: " + drop + '\n')
                            LOGGING_FILE.write("Chek: " + drops[loc] + '\n')
                            if drop in drops[loc]:
                                drop_data = drops[loc].split(":")
                                drop_data[1] = int(drop_data[1]) + 1
                                drops[loc] = "" + drop_data[0] + ":" + str(drop_data[1])
                                existing_drop = True
                        if not existing_drop:
                            drops.append(drop + ":1\n")
                            LOGGING_FILE.write(drop + " appended." + '\n\n')
                    elif 'XP' in event['title']:
                        LOGGING_FILE.write("XP MILESTONE\n")
                        xp_data = xp_info.split(":")
                        xp_data[1] = int(xp_data[1]) + 1
                        xp_info = "Experience milestones:" + str(xp_data[1])
                        xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "w")
                        xp_log.write(xp_info)
                        xp_log.close()
                    else:
                        remaining_events = events[idx:]
                        utd = True
                        for e in remaining_events:
                            if e not in re_list:
                                utd = False
                        if utd:
                            return
            if reprint_drops:
                drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "w")
                for d in drops:
                    if d.__len__() > 5:
                        LOGGING_FILE.write("Drop written to log: " + d + '\n')
                        if '\n' not in d:
                            drop_log.write(d + '\n')
                        else:
                            drop_log.write(d)


        else:
            LOGGING_FILE.write("File empty\n")
            recent_items = None

            user_log.write("Adventurer's Log: " + rsn + "\n")

            for event in events:
                new_event = event['title'] + ": " + event['description'] + '\n'
                user_log.write(new_event)
                LOGGING_FILE.write(event['title'] + '\n')

                if 'I found' in event['title']:
                    if 'a pair of' in event['title']:
                        title = event['title'].split(' ', 5)
                        drop = title[5]
                        drop = drop.strip('.')
                    elif (' a ' in event['title']) or (' an ' in event['title']):
                        title = event['title']
                        title = title.split(' ', 3)
                        drop = title[3]
                        drop = drop.strip(".")
                    else:
                        title = event['title']
                        title = title.split(' ', 2)
                        drop = title[2]
                        drop = drop.strip(".")

                    existing_drop = False
                    for loc, x in enumerate(drops):
                        LOGGING_FILE.write("Drop: " + drop + '\n')
                        LOGGING_FILE.write("Chek: " + drops[loc] + '\n')
                        if drop in drops[loc]:
                            drop_data = drops[loc].split(":")
                            drop_data[1] = int(drop_data[1]) + 1
                            drops[loc] = "" + drop_data[0] + ":" + str(drop_data[1]) + "\n"
                            existing_drop = True
                    if not existing_drop:
                        drops.append(drop + ":1\n")
                        LOGGING_FILE.write(drop + " appended.\n\n\n")

                if 'XP' in event['title']:
                    LOGGING_FILE.write("XP MILESTONE\n")
                    xp_data = xp_info.split(":")
                    xp_data[1] = int(xp_data[1]) + 1
                    xp_info = "Experience milestones:" + str(xp_data[1])
                    xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "w")
                    xp_log.write(xp_info)
                    xp_log.close()

            drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "w")
            for d in drops:
                if d.__len__() > 5:
                    #print(d)
                    drop_log.write(d)

        check_user_file.close()
        drop_log.close()
        user_log.close()

        LOGGING_FILE.write("")


def update_logs():
    tracking_roster = open(os.path.join(sys.path[0], "alogs/roster.txt"), "r")
    roster = tracking_roster.read()
    tracking_roster.close()

    users = roster.split('\n')

    for user in users:
        user.strip('\n')
        if user.__len__() >= 1:
            track_user(user)

    LOGGING_FILE = open("alog_beta_log.txt", 'a')
    LOGGING_FILE.write('--------------------------------------------------------------------------\n'
                       'END OF LOG UPDATES\n'
                       '--------------------------------------------------------------------------\n')
    LOGGING_FILE.close()


def reset_user(rsn):
    adv_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "adv_log" + ".txt"), "w")
    drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "w")
    xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "w")
    xp_log.write("Experience milestones:0")

    adv_log.close()
    drop_log.close()
    xp_log.close()


def setup(client):
    client.add_cog(Alog(client))
