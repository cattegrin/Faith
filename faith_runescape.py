import urllib
import xmltodict
import os
import sys
import re
import runescapeapi
from faith_utilities import tail


page = 'http://services.runescape.com/m=adventurers-log/c=tB0ermS1flc/rssfeed?searchName=Jaycole'

rss_feed = urllib.request.urlopen(page)
data = rss_feed.read()
rss_feed.close()

data = xmltodict.parse(data)

data_table = data['rss']['channel']

events = data_table['item']

#opens relevant files
try:
    user_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "adv_log" + ".txt"), "a")
    drop_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "drop_log" + ".txt"), "r+")
    xp_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "xp_log" + ".txt"), "r+")
    check_user_file = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "adv_log" + ".txt"), "r")
except FileNotFoundError:
    try:
        os.mkdir("alogs/Jaycole/")
        user_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "adv_log" + ".txt"), "a")
        drop_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "drop_log" + ".txt"), "r+")
        xp_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "xp_log" + ".txt"), "r+")
        check_user_file = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "adv_log" + ".txt"), "r")
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
    drop_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "drop_log" + ".txt"), "w")
    drops = []

#checks if user has stored alog
if(check_user_file.readline().__len__() > 2):
    recent_items = tail("alogs/Jaycole/" + "adv_log" + ".txt", 20)
    print("--------------------------------------------")
    print(recent_items)
    print("--------------------------------------------")

    re = recent_items[0]
    re_list = re.split('\n')

    reprint_drops=False
    for idx, a in enumerate(events):
        event = events[idx]
        new_event = event['title'] + ": " + event['description']

        if new_event not in re_list:
            user_log.write(new_event + '\n')

            if 'I found' in event['title']:
                reprint_drops=True
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
                        drops[loc] = "" + drop_data[0] + ":" + drop_data[1]
                        existing_drop=True
                if not existing_drop:
                    drops.append(drop + ":1\n")
                    print(drop + " appended.")

            if 'XP' in event['title']:
                print("XP MILESTONE")
                xp_data = xp_info.split(":")
                xp_data[1] = int(xp_data[1]) + 1
                xp_info = "Experience milestones:" + str(xp_data[1])
                xp_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "xp_log" + ".txt"), "w")
                xp_log.write(xp_info)
                xp_log.close()

    if reprint_drops:
        drop_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "drop_log" + ".txt"), "w")
        for d in drops:
            if d.__len__() > 5:
                print(d)
                drop_log.write(d)


else:
    print("File empty")
    recent_items = None

    user_log.write("Adventurer's Log: " + " Jaycole\n")

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
            xp_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "xp_log" + ".txt"), "w")
            xp_log.write(xp_info)
            xp_log.close()

    drop_log = open(os.path.join(sys.path[0], "alogs/Jaycole/" + "drop_log" + ".txt"), "w")
    for d in drops:
        if d.__len__() > 5:
            print(d)
            drop_log.write(d)


check_user_file.close()
drop_log.close()
user_log.close()




