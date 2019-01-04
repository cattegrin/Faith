import urllib
import xmltodict
import os
import sys
from faith_utilities import get_rsn
from faith_utilities import say
from faith_utilities import tail
from discord.ext import commands


class Alog:
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
            await self.client.say(alog_help)
            return

        args = argv.split(' ')
        rsn = get_rsn(context.message.author.mention)
        if args[0] == 'activate':
            user_tracking = active_tracking(rsn)
            if user_tracking is True:
                await self.client.say("User " + rsn + " added to active tracking roster.")
            else:
                await self.client.say("I'm already keeping track of your adventurer log " + rsn)
        elif args[0] == 'track':
            track(self.client, rsn)

def track(client, rsn):
    tracking_roster = open(os.path.join(sys.path[0], "alogs/roster.txt"), "a")
    roster = tracking_roster.read()
    tracking_roster.close()

    if rsn in roster:
        track_user(rsn)
        say(client, "User " + rsn + "'s Adventurer Log has been updated.")
    else:
        say(client, "Your adventures are not currently being tracked. Please enable tracking by doing ::alog activate")


def active_tracking(rsn):
    tracking_roster = open(os.path.join(sys.path[0], "alogs/roster.txt"), "r")
    roster = tracking_roster.read()
    tracking_roster.close()

    if rsn not in roster:
        tracking_roster = open(os.path.join(sys.path[0], "alogs/roster.txt"), "a")
        tracking_roster.write(rsn + '\n')
        tracking_roster.close()

        os.mkdir("alogs/" + rsn + "/")
        drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "w")
        xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "w")
        xp_log.write("Experience milestones:0")

        drop_log.close()
        xp_log.close()

        track_user(rsn)
        return True
    else:
        return False


def track_user(rsn):

        if ' ' in rsn:
            rsn_split = rsn.split(" ")
            rsn_append = ''

            for substr in rsn_split:
                rsn_append += substr + '%20'
        else:
            rsn_append = rsn

        user_page = 'http://services.runescape.com/m=adventurers-log/c=tB0ermS1flc/rssfeed?searchName=' + rsn_append
        rss_feed = urllib.request.urlopen(user_page)
        data = rss_feed.read()
        rss_feed.close()

        data = xmltodict.parse(data)

        data_table = data['rss']['channel']

        events = data_table['item']

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
                print("Creation of the directory failed")

        try:
            drop_list = drop_log.read()
            drops = drop_list.split('\n')
            drop_log.close()

            xp_info = xp_log.read()
            xp_log.close()
        except NameError:
            print("Name Error")
            sys.exit()

        # checks if user has stored alog
        if check_user_file.readline().__len__() > 2:
            recent_items = tail("alogs/" + rsn + "/" + "adv_log" + ".txt", 20)

            re = recent_items[0]
            re_list = re.split('\n')

            reprint_drops = False
            for idx, a in enumerate(events):
                event = events[idx]
                new_event = event['title'] + ": " + event['description']

                if new_event not in re_list:
                    user_log.write(new_event + '\n')

                    if 'I found' in event['title']:
                        if 'a pair of' in event['title']:
                            title = title.split(' ', 5)
                            drop = title[5]
                        else:
                            title = event['title']
                            title = title.split(' ', 3)
                            drop = title[3]
                            drop = drop.strip(".")

                        reprint_drops = True

                        existing_drop = False
                        for loc, x in enumerate(drops):
                            print("Drop: " + drop)
                            print("Chek: " + drops[loc])
                            if drop in drops[loc]:
                                drop_data = drops[loc].split(":")
                                drop_data[1] = int(drop_data[1]) + 1
                                drops[loc] = "" + drop_data[0] + ":" + drop_data[1]
                                existing_drop = True
                        if not existing_drop:
                            drops.append(drop + ":1\n")
                            print(drop + " appended.")
                else:
                    remaining_events = events[idx:]
                    utd = True
                    for e in remaining_events:
                        if e not in re_list:
                            utd = False
                    if utd:
                        break


                    if 'XP' in event['title']:
                        print("XP MILESTONE")
                        xp_data = xp_info.split(":")
                        xp_data[1] = int(xp_data[1]) + 1
                        xp_info = "Experience milestones:" + str(xp_data[1])
                        xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "w")
                        xp_log.write(xp_info)
                        xp_log.close()

            if reprint_drops:
                drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "w")
                for d in drops:
                    if d.__len__() > 5:
                        print(d)
                        drop_log.write(d)


        else:
            print("File empty")
            recent_items = None

            user_log.write("Adventurer's Log: " + rsn + "\n")

            for event in events:
                new_event = event['title'] + ": " + event['description'] + '\n'
                user_log.write(new_event)
                print(event['title'])

                if 'I found' in event['title']:
                    title = event['title']
                    title = title.split(' ', 3)
                    drop = title[3]
                    drop = drop.strip(".")
                    print(drop)

                    existing_drop = False
                    for loc, x in enumerate(drops):
                        print("Drop: " + drop)
                        print("Chek: " + drops[loc])
                        if drop in drops[loc]:
                            drop_data = drops[loc].split(":")
                            drop_data[1] = int(drop_data[1]) + 1
                            drops[loc] = "" + drop_data[0] + ":" + str(drop_data[1]) + "\n"
                            existing_drop = True
                    if not existing_drop:
                        drops.append(drop + ":1\n")
                        print(drop + " appended.")

                if 'XP' in event['title']:
                    print("XP MILESTONE")
                    xp_data = xp_info.split(":")
                    xp_data[1] = int(xp_data[1]) + 1
                    xp_info = "Experience milestones:" + str(xp_data[1])
                    xp_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "xp_log" + ".txt"), "w")
                    xp_log.write(xp_info)
                    xp_log.close()

            drop_log = open(os.path.join(sys.path[0], "alogs/" + rsn + "/" + "drop_log" + ".txt"), "w")
            for d in drops:
                if d.__len__() > 5:
                    print(d)
                    drop_log.write(d)

        check_user_file.close()
        drop_log.close()
        user_log.close()


def setup(client):
    client.add_cog(Alog(client))
