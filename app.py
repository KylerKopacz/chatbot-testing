import os
import sys
from time import gmtime, strftime
from bs4 import BeautifulSoup
import requests

from flask import Flask, request

app = Flask(__name__)

location_coords = {'x': '42.372400734', 'y': '-72.516410713'}
location_name = "Amherst"


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # We don't want to reply to ourselves!
    msg = parse_message(data)
    send_message(msg)

    return "ok", 200


def parse_message(data):
    if data['text'].strip() == '!Weather':
        msg = getWeather()
    elif data['text'].strip() == '!Hello':
        msg = "Hey {}!".format(data['name'])
    elif data['text'].strip() == '!Breakfast':
        msg = getMeal('Breakfast')
    elif data['text'].strip() == '!Lunch':
        msg = getMeal('Lunch')
    elif data['text'].strip() == '!Dinner':
        msg = getMeal('Dinner')
    elif data['text'].strip() == '!Help':
        msg = '''
Hi! I am Brobot, an assistant for this groupchat.
Try out some of the following commands and I can gather some information for you:

"!Weather" - Get the current and future weather for Amherst College

"!Hello" - Just to say hi

"!Breakfast/Lunch/Dinner" - to get the Valentine Dining Hall meals for the specified meal

"!Help" - print out some help for using me
    '''

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