# all the import statements
import os
import sys
from time import gmtime, strftime
from bs4 import BeautifulSoup
import requests
from flask import Flask, request
from pathlib import Path


# global variables to be used by the app later. We could just put them into the
# functions, maybe ill do that later
app = Flask(__name__)
location_coords = {'x': '42.372400734', 'y': '-72.516410713'}
location_name = "Amherst"
schedule_path = Path("schedule.txt")



@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # We don't want to reply to ourselves!
    msg = parse_message(data)
    send_message(msg)

    return "ok", 200


def parse_message(data):
    recievedMessage = data['text'].split('\n')

    if recievedMessage[0].lower().strip() == '!weather':
        msg = getWeather()
    elif recievedMessage[0].lower().strip() == '!hello':
        msg = "Hey {}!".format(data['name'])
    elif recievedMessage[0].lower().strip() == '!breakfast':
        msg = getMeal('Breakfast')
    elif recievedMessage[0].lower().strip() == '!lunch':
        msg = getMeal('Lunch')
    elif recievedMessage[0].lower().strip() == '!dinner':
        msg = getMeal('Dinner')
    elif recievedMessage[0].lower().strip() == '!gng':
        msg = getGNG()
    elif recievedMessage[0].lower().strip() == '!setschedule':
        msg = writeSchedule(recievedMessage)
    elif recievedMessage[0].lower().strip() == "!schedule":
        msg = getSchedule()
    elif recievedMessage[0].lower().strip() == '!help':
        msg = '''
BrotherBot v1.12.0 Commands:

"!Weather" - Get the current and future weather for Amherst College

"!Hello" - Just to say hi

"!Breakfast/Lunch/Dinner" - to get the Valentine Dining Hall meals for the specified meal

"!gng" - to get the Grab and Go Menu for the day

"!setschedule <schedule>" - save a schedule

"!schedule" - print out the saved schedule

"!Help" - print out some help for using broterbot
    '''

    # return the message to be printed out
    return msg


def send_message(msg):
    url = "https://api.groupme.com/v3/bots/post"

    data = {
        "bot_id": os.getenv('GROUPME_BOT_ID'),
        "text": msg,
    }
    requests.post(url, data)


def getWeather():
    r = requests.get('https://api.weather.gov/points/' + location_coords['x'] + ',' + location_coords['y'] + '/forecast')
    weather_response = r.json()

    current_weather = weather_response['properties']['periods'][0]['detailedForecast']
    weather_time = weather_response['properties']['periods'][0]['name']

    future_weather = weather_response['properties']['periods'][1]['detailedForecast']
    future_weather_time = weather_response['properties']['periods'][1]['name']


    msg = "The " + weather_time + " forecast in " + location_name + ": " + current_weather + "\n\n"
    msg += "The " + future_weather_time + " forecast in " + location_name + ": " + future_weather

    return msg

def getMeal(meal):
    # get the current time to pass into the val page
    date = strftime("%Y-%m-%d", gmtime())

    # get the current val page
    msg = ''
    counter = 0
    page = requests.get('https://www.amherst.edu/campuslife/housing-dining/dining/menu')
    soup = BeautifulSoup(page.content, 'html.parser')
    for meal in soup.find_all(id='dining-menu-' + date + '-' + meal):
        for string in meal.strings:
            if counter % 2 == 1 or counter == 0:
                string += ':'
            counter += 1
            msg += string + '\n\n'
    return msg

def getGNG():
    # get the current time to pass into the val page
    date = strftime("%Y-%m-%d", gmtime())

    # get the current grab and go page
    msg = 'Grab and Go Hours (Typically) 11:00am - 2:30pm Monday - Friday\n\n'
    counter = 0
    page = requests.get('https://www.amherst.edu/campuslife/housing-dining/dining/dining-options-and-menus/grabngo/Menus')
    soup = BeautifulSoup(page.content, 'html.parser')
    for meal in soup.find_all(id='dining-menu-' + date + '-grab-n-go-link-menu-listing'):
        for string in meal.strings:
            if counter % 2 == 0:
                string += ':'
            counter += 1
            msg += string + '\n\n'
    return msg

def writeSchedule(messageList):
    # parse the message
    lines = [line for line in messageList if line != '']
    lines.remove('!setschedule')
    finalSchedule = ""
    for i in lines:
        finalSchedule += i + '\n'

    # write that final message to a file
    with open(schedule_path, 'w') as schedule:
        schedule.write(finalSchedule)

    return "Schedule successfully saved."

def getSchedule():
    if schedule_path.is_file():
        with open(schedule_path, 'r') as file:
            schedule = file.read()
            return schedule
    else:
        return "No saved schedule found. Run !setschedule <schedule> to save a schedule."