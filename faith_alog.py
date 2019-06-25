import urllib
import os
import sys
import datetime
import xmltodict
import time

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
            await context.message.channel.send(track(self.client, context.message.channel, rsn))
        elif args[0] == 'drops':
            await context.message.channel.send("Getting drops for " + rsn)
            await context.message.channel.send(pull_drops(rsn))
        elif args[0] == 'xp':
            await context.message.channel.send("Getting XP milestones for " + rsn)
            await context.message.channel.send(pull_xp(rsn))
        elif args[0] == 'full':
            alog = (pull_alog(rsn))
            log = alog.split('\n')
            max = 10
            n = 0
            line = ""
            #items = [log[i:i + n] for i in range(0, len(log), n)]
            for item in log:
                line += item + '\n'
                n += 1
                if n == max:
                    await context.message.author.send(line)
                    line = ""
                    n = 0
                    time.sleep(2)

            await context.message.channel.send("Check your private messages to see your full Adventurer's Log")
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


def track(client, channel, rsn):
    print("Track request received")
    tracking_roster = open(os.path.join(sys.path[0], "alogs/roster.txt"), "r")
    roster = tracking_roster.read()
    print("Roster Saved")
    tracking_roster.close()

    if rsn in roster:
        track_user(rsn)
        return("User " + rsn + "'s Adventurer Log has been updated.")
    else:
        return("Your adventures are not currently being tracked. Please enable tracking by doing ::alog activate")


def pull_drops(rsn):
    drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "r")
    drops = drop_log.read()
    drop_log.close()
    return("```------Drop List for " + rsn + '------\n' + drops + "---------------------------------```")


def pull_alog(rsn):
    user_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "adv_log" + ".txt"), "r")
    log = user_log.read()
    user_log.close()
    return ("```------Adventurer's Log  for " + rsn + '------\n' + log + "---------------------------------```")


def pull_xp(rsn):
    xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "r")
    xp_line = xp_log.read()
    xp_log.close()

    xp = xp_line.split(':')

    return ("You have achieved " + xp[1] + " experience milestones since I started following your adventures, " + rsn + '.')


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
                user_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "adv_log" + ".txt"), "w+")
                drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "w+")
                xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "w+")
                check_user_file = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "adv_log" + ".txt"), "w+")
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
            LOGGING_FILE.write("Path: " + "alogs/" + rsn + "/" + "adv_log" + ".txt\n")
            recent_items = tail("alogs/" + rsn + "/" + "adv_log" + ".txt", 5)

            try:
                if recent_items[0] is None:
                    LOGGING_FILE.write("SEEK ERROR: Caused during tail of " + rsn +"'s log.")
                    return
            except IndexError:
                LOGGING_FILE.write("INDEX ERROR: Caused during tail of " + rsn + "'s log.")
                return

            new_events = []
            for event in events:
                event_data = event['title'] + ":" + event['description']
                if event_data not in recent_items:
                    new_events.append(event_data)
                    user_log.write(event_data)

            for event in new_events:
                if 'experience points' in event:
                    xp_data = xp_info.split(':')
                    xp_data[1] = str(int(xp_data[1]) + 1)
                    xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "w")
                    xp_log.write(xp_data[0] + ':' + xp_data[1])
                    xp_log.close()
                elif 'I found' in event:
                    drop_data = event.split(':')
                    new_drop = drop_data[0]
                    try:
                        if drop_data[2] is not None:
                            new_drop += ":" + drop_data[1]
                    except IndexError:
                        pass

                    LOGGING_FILE.write("New drop: " + new_drop + "\n")
                    for old_drop in drops:
                        utd = False
                        old_drop_data = old_drop.split(':')
                        old = old_drop_data[0]
                        try:
                            if old_drop_data[2] is not None:
                                old += ':' + old_drop_data[1]
                        except IndexError:
                            pass

                        if new_drop == old:
                            old_drop_data[1] = str(int(old_drop_data[-1]) + 1)
                            utd = True
                            LOGGING_FILE.write("Drop counter incremented.\n")
                            break
                    if utd is False:
                        if 'pet' in new_drop:
                            drops.append(new_drop)
                        else:
                            drops.append(new_drop + ":1")
                        LOGGING_FILE.write("New drop added to counter.\n")

                    drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "w")
                    for drop in drops:
                        drop_data = drop.split(':')
                        print(drop_data)
                        print("\n\n")
                        try:
                            if drop_data[2] is not None:
                                write_drop = drop_data[0] + ": " + drop_data[1] + ":" + drop_data[2]
                        except IndexError:
                            try:
                                write_drop = drop_data[0] + ":" + drop_data[1]
                            except IndexError:
                                write_drop = drop_data[0]

                        drop_log.write(write_drop + "\n")

        check_user_file.close()
        xp_log.close()
        drop_log.close()

        LOGGING_FILE.write("")
        LOGGING_FILE.close()


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
