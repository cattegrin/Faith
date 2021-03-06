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
                      brief='Updates the news feed.',
                      pass_context=True)
    async def checknews(self, context):
        await check_news_feed(self.client)
        print("News feed updated.\n")



async def check_news_feed(client):
    news = client.get_channel(id=579125498781630467)

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

    archive_file = open("news_archive.txt", "r")
    archive_items = archive_file.read()
    archive_file.close()

    if archive_items != None:
        archive = archive_items.split('\n')
    else:
        archive = ""

    archive_add = open("news_archive.txt", "a")

    for idx, a in enumerate(articles):
        article = articles[idx]
        new_article = "**" + article['title'] + "**\n" + article['description'] + "\nRead Here: " + article['link'] + "\n"
        title = "**" + article['title'] + "**";

        if title not in archive:
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
        if channel is None:
            print("Channel is none.")
        else:
            print("Channel is not none.")


def setup(client):
    client.add_cog(RsNewsFeed(client))
