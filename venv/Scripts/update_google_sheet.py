import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def update_sheet(player_rsn):
    player_rsn = sys.argv[0]

    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

    try:    #creates client and opens rank spreadsheet
        g_client = gspread.authorize(creds)
        sheet = g_client.open("RuneScape Clan Ranks by Points").get_worksheet(1)
    except:
        print ("Client operation failed.")
        return

    # updates user points
    print(player_rsn)
    row = sheet.find(player_rsn).row
    print("Row: " + str(row))
    print("Points: " + (sheet.cell(row, 6).value))
    sheet.update_cell(row, 7, int(sheet.cell(row, 6).value) + 5)

    sys.exit()
