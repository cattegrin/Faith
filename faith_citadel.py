from discord.ext import commands
from faith_user import get_rsn
from oauth2client.service_account import ServiceAccountCredentials
import gspread


class Citadel:
    def __init__(self, client):
        self.client = client
        self.counter = 0

    @commands.command(name='citadel_manual_reset',
                    brief='Admin command to manually reset capped log.',
                    pass_context=True)
    async def citadel_manual_reset(self, context):
        user_roles = context.message.author.roles  # gets user role list
        for role in user_roles:  # loops through user roles
            if '🗝️ FiH Leader' == role.name or 'Beta' in role.name:
                clear_capped = open('capped.txt', 'w')  # clears list file
                # write next build tick time
                clear_capped.close()  # closes list

                self.client.say("Capped log manually reset.")

    @commands.command(name='capped',
                    brief='Reports that you capped at the citadel this week.',
                    pass_context=True)
    async def capped(self, context):
        player_rsn = get_rsn(context.message.author.mention)  # gets RSN of player
        if player_rsn is None:  # checks to see that RSN has been set
            await self.client.say(
                "Hey " + context.message.author.mention + ", please set your rsn before using this command. "
                                                          "You can set it by doing ::setrsn <name>.")
            return  # exits function

        capped = open('capped.txt', 'r')  # opens list of capped users
        capped_list = capped.read()  # reads in capped users
        capped.close()  # closes list

        if player_rsn in capped_list:  # checks if player has already capped
            await self.client.say("Hey " + player_rsn + ", you've already capped this week.")
            return

        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

        try:  # creates client and opens rank spreadsheet
            g_client = gspread.authorize(creds)
            sheet = g_client.open("RuneScape Clan Ranks by Points").get_worksheet(1)

            # updates user points
            row = sheet.find(player_rsn).row
            sheet.update_cell(row, 7, int(sheet.cell(row, 7).value) + 5)

            capped_write = open('capped.txt', 'a')  # opens capped list in append mode
            capped_write.write(player_rsn + '\n')  # adds user to list
            capped_write.close()  # closes list

            await self.client.say("Thanks for capping " + player_rsn + "!")  # thanks the player for capping
        except:
            print("Client operation failed.")

            await self.client.say("Hey " + get_rsn(
                context.message.author.mention) + ", there was an error adding your points to the spreadsheet. Please check that the name you set with ::setrsn matches your actual RSN (CaSe SeNSiTiVE")
            return


def citadel_reset():
    capped_list = open('capped.txt', 'r')           #opens capped list
    capped_users = capped_list.read()               #gets users who capped
    capped_list.close()                             #closes list

    clear_capped = open('capped.txt', 'w')      #clears list file
    clear_capped.close()                        #closes list


def setup(client):
    client.add_cog(Citadel(client))