#!/usr/bin/python

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import time
import Adafruit_CharLCD as LCD
from multiprocessing import Process

import gpiozero

def initLED():
    blue = gpiozero.LED(3)
    red = gpiozero.LED(4)
    return {'blue':blue,'red':red}

def initLCD():
    # LCD Pinout
    # Vss | Vdd | Vo  | RS  | R/W | E   | DB0 | DB1 | DB2 | DB3 | DB4 | DB5 | DB6 | DB7 | A   | K   
    # GND | 5V  | POT | YEL | GND | GRN | -   | -   | -   | -   | BL1 | BL2 | ORG | WHT | 5V  | GND

    # Pi Pinout
    # 5V  | 5V  | GND | G14 | G15 | G18 | GND | G23 | G24 | GND | G25 | G8  | ...
    # -   | 5V  | GND | WHT | ORG | BL2 | GND | BL1 | GRN | GND | YEL | -   | ...

    # Raspberry Pi pin configuration:
    lcd_rs        = 25#27  # Note this might need to be changed to 21 for older revision Pi's.
    lcd_en        = 24#22
    lcd_d4        = 23#25
    lcd_d5        = 18#24
    lcd_d6        = 15#23
    lcd_d7        = 14#18
    lcd_backlight = 4

    # Define LCD column and row size for 16x2 LCD.
    lcd_columns = 16
    lcd_rows    = 2

    # Initialize the LCD using the pins above.
    lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

    # Print a two line message
    lcd.message('  Launch Point  \n3D Printer Jobs!')

    # Wait 5 seconds
    time.sleep(3.0)

    return lcd

def initGoogleAPI():
    # Setup the Sheets API
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('/home/pi/Documents/Git/Adafruit_Python_CharLCD/examples/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('/home/pi/Documents/Git/Adafruit_Python_CharLCD/examples/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    status = {'uPrint':{},'Objet':{},'Markforged':{}}
    return [status,service]

def demo():
    lcd.clear()
    lcd.message(' Test  \nMessage')

    i=0
    while 1:
        if i==10:
            i=0
            lcd.clear()
            lcd.message('Repeat')
        elif i%2==0:
            lcd.clear()
            lcd.message('Test 1')
        else:
            lcd.clear()
            lcd.message('Test 2')
        time.sleep(2.0)
        i=i+1

def readSpreadsheet(status,service):
    workToDo = {'quotes':0,'ready':0}
    for printer in status:
        RANGE_NAME = printer+' Printer!A3:W'
        SPREADSHEET_ID = "1P765kN5YrMqTB38tYyli0awB_eB7mztQGyXAS8zKnIA"
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        pendingQuotes = 0 
        readyToPrint = 0

        if not values:
            print('   No data found.')
        else:
            for row in values:
                if row[0]:
                    if "Pending Quote" in row[0]:
                        pendingQuotes = pendingQuotes + 1
                        workToDo['quotes'] = 1
                    elif "Ready To Print" in row[0]:
                        readyToPrint = readyToPrint + 1
                        workToDo['ready'] = 1
            status[printer]={'pendingQuote':pendingQuotes, 'readyToPrint':readyToPrint}
    print('Ready: '+str(workToDo['ready'])+'   Quote: '+str(workToDo['quotes'])+'\n')
    return [status,workToDo]

def displayStatus(mode,status,lcd):
    # ################
    # ################
    lcd.clear()
    if mode==0:
        # Print | uP Ob Mf
        # Ready | ## ## ##
        message = ("Print | uP Ob Mf\nReady | %02d %02d %02d" % (status['uPrint']['readyToPrint'],status['Objet']['readyToPrint'],status['Markforged']['readyToPrint']))
    elif mode==1:
        # Needs | uP Ob Mf
        # Quote | ## ## ##
        message = ("Needs | uP Ob Mf\nQuote | %02d %02d %02d" % (status['uPrint']['pendingQuote'],status['Objet']['pendingQuote'],status['Markforged']['pendingQuote']))
    print(message+'\n')
    lcd.message(message)

if __name__ == '__main__':
    LCD = initLCD()
    LED = initLED()
    [STATUS,SERVICE] = initGoogleAPI()
    [STATUS,WORKTODO] = readSpreadsheet(STATUS,SERVICE)
    print(STATUS)
    MODE=0
    i = 1
    while(1):
        displayStatus(MODE,STATUS,LCD)
        time.sleep(3.0)
        MODE = not MODE
        if i%20==0:
            [STATUS,WORKTODO] = readSpreadsheet(STATUS,SERVICE)
        
        if(WORKTODO['quotes']==0 and WORKTODO['ready']==0):
            LED['red'].off()
            LED['blue'].off()
        elif(WORKTODO['quotes']==1 and WORKTODO['ready']==0):
            LED['red'].off()
            LED['blue'].on()
        elif(WORKTODO['quotes']==0 and WORKTODO['ready']==1):
            LED['red'].on()
            LED['blue'].off()
        else:
            LED['red'].on()
            LED['blue'].on()
        
        i=i+1
