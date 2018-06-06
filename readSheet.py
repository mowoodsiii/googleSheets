from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

SPREADSHEET_ID = "1P765kN5YrMqTB38tYyli0awB_eB7mztQGyXAS8zKnIA"
#SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
#result = service.spreadsheets().values().get(sheetID=

status = {'uPrint':{},'Objet':{},'Markforged':{}}
for printer in status:
    RANGE_NAME = printer+' Printer!A3:W'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                         range=RANGE_NAME).execute()
    values = result.get('values', [])
    pendingQuotes = 0 
    readyToPrint = 0

    if not values:
        print('   No data found.')
    else:
        #print('Status / Name')
        for row in values:
            if row[0]:
                # Print columns A and E, which correspond to indices 0 and 4.
                #print('%s, %s' % (row[0], row[8]))
                if "Pending Quote" in row[0]:
                    pendingQuotes = pendingQuotes + 1
                elif "Ready To Print" in row[0]:
                    readyToPrint = readyToPrint + 1
        status[printer]={'pendingQuote':pendingQuotes, 'readyToPrint':readyToPrint}

# ################
# ################

# Print | uP Ob Mf
# Ready | ## ## ##
print("Print | uP Ob Mf\nReady | %02d %02d %02d" % (status['uPrint']['readyToPrint'],status['Objet']['readyToPrint'],status['Markforged']['readyToPrint']))

print('')

# Needs | uP Ob Mf
# Quote | ## ## ##
print("Needs | uP Ob Mf\nQuote | %02d %02d %02d" % (status['uPrint']['pendingQuote'],status['Objet']['pendingQuote'],status['Markforged']['pendingQuote']))
