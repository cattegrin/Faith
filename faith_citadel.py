from discord.ext import commands
from faith_user import get_rsn
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import datetime


class Citadel(commands.Cog):
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
                citadel_reset()

                await context.message.channel.send("Capped log manually reset.")

    @commands.command(name='capped',
                    brief='Reports that you capped at the citadel this week.',
                    pass_context=True)
    async def capped(self, context):
        capped = open('capped.txt', 'r')  # opens list of capped users
        capped_list = capped.read()  # reads in capped users
        capped.close()  # closes list

        day = datetime.datetime.today()
        if(("Reset: " + day.now().strftime("%Y-%m-%d")) not in capped_list) and (datetime.datetime.today().weekday() == 6):
            citadel_reset()

        player_rsn = get_rsn(context.message.author.mention)  # gets RSN of player
        if player_rsn is None:  # checks to see that RSN has been set
            await context.message.channel.send(
                "Hey " + context.message.author.mention + ", please set your rsn before using this command. "
                                                          "You can set it by doing ::setrsn <name>.")
            return  # exits function

        if player_rsn in capped_list:  # checks if player has already capped
            await context.message.channel.send("Hey " + player_rsn + ", you've already capped this week.")
            return

        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

        try:  # creates client and opens rank spreadsheet
            g_client = gspread.authorize(creds)
            sheet = g_client.open("RuneScape Clan Ranks by Points").get_worksheet(1)

            # updates user points
            user_list = sheet.col_values(1)
            if player_rsn in user_list:
                row = sheet.find(player_rsn).row
                sheet.update_cell(row, 7, int(sheet.cell(row, 7).value) + 5)
            else:
                row = user_list.__len__() + 1
                sheet.update_cell(row, 1, player_rsn)
                sheet.update_cell(row, 7, 5)
                await self.client.send_message(context.message.channel.server.owner,
                                         player_rsn + " not found on rank sheet, attempting to update...")

            capped_write = open('capped.txt', 'a')  # opens capped list in append mode
            capped_write.write(player_rsn + '\n')  # adds user to list
            capped_write.close()  # closes list

            await context.message.channel.send("Thanks for capping " + player_rsn + "!")  # thanks the player for capping
        except:
            print("Client operation failed.")

            await context.message.channel.send("Hey " + get_rsn(
                context.message.author.mention) + ", there was an error adding your points to the spreadsheet. Please check that the name you set with ::setrsn matches your actual RSN (CaSe SeNSiTiVE")
            return



def citadel_reset():
    clear_capped = open('capped.txt', 'w')      #clears list file
    clear_capped.write("Reset:" + datetime.datetime.today().now().strftime("%Y-%m-%d") + '\n')
    clear_capped.close()                        #closes list


def setup(client):
    client.add_cog(Citadel(client))