import urllib
import xmltodict
from discord.ext import commands
from discord import client
import os
import sys
from xml.parsers.expat import ExpatError
from faith_utilities import tail


class RsNewsFeed(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.counter = 0

    @commands.command(name='checknews',
                      brief='Updates the news feed. .',
                      pass_context=True)
    async def checknews(self, context):
        check_news_feed()
        print("News feed updated.\n")



async def check_news_feed(client):
    news = client.get_channel(id=576171984036298772)
    print(news)

    page = "https://secure.runescape.com/m=news/latest_news.rss"

    rss_feed = urllib.request.urlopen(page)
    data = rss_feed.read()
    rss_feed.close()

    try:
        dict_data = xmltodict.parse(data)
    except ExpatError:
        print("Data could not be processed \n" + data)


    data_table = dict_data['rss']['channel']

    articles = data_table['item']
    archive_items = tail("news_archive.txt", 10)

    if archive_items != None:
        a = archive_items[0]
        archive = a.split('\n')
        print(archive)
    else:
        archive = ""

    archive_add = open("news_archive.txt", "a")

    for idx, a in enumerate(articles):
        article = articles[idx]
        new_article = article['title'] + ": " + article['description'] + "\nRead Here: " + article['link'] + " \n"

        if new_article not in archive:
            archive_add.write(new_article)
            await send_news(news, new_article)
        else:
            break

    archive_add.close()

async def send_news(channel, article):

    try:
        await channel.send(article)
    except AttributeError:
        print("Attribute Error")
        if(channel == None):
            print("Channel is none.")
        else:
            print("Channel is not none.")


def setup(client):
    client.add_cog(RsNewsFeed(client))
