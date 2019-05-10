import runescapeapi
from discord.ext import commands
from discord.utils import get
from faith_utilities import get_user
import sys
from faith_utilities import get_rsn

class rsAPI(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.counter = 0

    @commands.command(name='stats',
                      brief='Shows the stats of a given player.',
                      pass_context=True)
    async def stats(self, context):
        argv = context.message.content[8:]

        if len(argv) < 2:                               #did user not provide a name? look up self.
            rsn = get_rsn(context.message.author.mention)
            player = runescapeapi.Highscores(rsn)

        else:                                           #if user did provide a name
            rsn = argv
            print(rsn)
            argv.replace(" ", "%20")
            player = runescapeapi.Highscores(argv)

        stat_list = parse_stats(player.skills)
        total_level = parse_total(player.total)

        stat_line = "```\n------------------------------------------------\n"
        title =  "|" + "{:^46}".format(" Stats for " + rsn + " ") + "|"

        stat_line += title + "\n" + "|----------------------------------------------|\n"
        stat_line += "| {:^13} | {:>5} | {:>10} | {:>7} |".format("Skill", "Level", "XP", "Rank") + "\n"
        stat_line += "|----------------------------------------------|\n"

        for stat in stat_list:
            stat_line = stat_line + stat + "\n"

        stat_line += total_level
        stat_line += "\n------------------------------------------------```"
        await context.message.channel.send(stat_line)

        print(total_level)

def parse_stats(player_stats):
    skills = []
    experience = []
    levels = []
    ranks = []
    results = []

    for skill in player_stats:
        skills.append(skill.get('name'))
        levels.append(skill.get('level'))
        experience.append(skill.get('xp'))
        ranks.append(skill.get('rank'))

    x = 0
    while x < 27:
        res = ("| {:^13} | {:>5d} | {:>10d} | {:>7d} |").format(skills[x], levels[x], experience[x], ranks[x])
        results.append(res)
        print (results[x])
        x += 1


    return results


def parse_total(player_total):
    return ("| {:^13} | {:>5d} | {:>10d} | {:>7d} |".format(player_total.get("name"),
                                                           player_total.get("level"),
                                                           player_total.get("xp"),
                                                           player_total.get("rank")))



def setup(client):
    client.add_cog(rsAPI(client))
