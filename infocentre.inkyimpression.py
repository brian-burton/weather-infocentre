#!/usr/bin/python3

import requests
import sys
import os
import metofficekey_bb as metofficekey
from inky.inky_uc8159 import Inky
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from time import sleep

##### Function defs #####

def parseWeather(data: list) -> list:
  """ take MetOffice weatherdata and return the first four future entries"""
  forecast = []
  whichday = 0
  HOUR_IN_MINS = datetime.now().hour * 60
  for day in data:
    for entry in day['Rep']:
      # The forecast is laggy for the current day, so we need to discard past entries
      if ((whichday == 0) & (int(entry['$']) < HOUR_IN_MINS)):
        pass
      # We only need 4 for a 12 hour forecast
      elif len(forecast) < 4:
        forecast.append(entry)
      # Throw the rest away
      else:
        pass
    whichday += 1
  return forecast

def buildWeatherTypes() -> list:
  """Build list of weather types"""
  weatherTypeList = []
  for text in ["\uF186","\uF185","\uF6C3","\uF6C4","UNUSED","\uF75F","\uF75F","\uF0C2","\uF0C2","\uF73C","\uF743","\uF73D","\uF73D","\uF740","\uF740","\uF740","\uF73B","\uF73B","\uF73B","\uF73B","\uF73B","\uF73B","\uF2DC","\uF2DC","\uF2DC","\uF2DC","\uF2DC","\uF2DC","\uF0E7","\uF0E7","\uF0E7"]:
    tmp = {'text': text}
    tmp['w'], tmp['h'] = ICON_FONT.getsize(text)
    weatherTypeList.append(tmp)
  return weatherTypeList

def getIndoorTempData() -> tuple:
  """Get the weather"""
  try:
    inData = requests.get(DOMOTICZ_URL + '?type=devices&rid=' + INDOOR_THERMO_ID).json()['result'][0]
    inTemp = str(inData['Temp'])
    inHumidity = str(inData['Humidity'])
  except:
    inTemp = "?.?"
    inHumidity = "?"
  return (inTemp, inHumidity)

def getOutdoorTempData() -> tuple:
  try:
    outData = requests.get(DOMOTICZ_URL + '?type=devices&rid=' + OUTDOOR_THERMO_ID).json()['result'][0]
    outTemp = str(outData['Temp'])
    outHumidity = str(outData['Humidity'])
  except:
    outTemp = "?.?"
    outHumidity = "?"
  return (outTemp, outHumidity)

##### Constants #####

DATAPOINT_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/" + metofficekey.LOCATION + "?res=3hourly&key=" + metofficekey.APIKEY
DOMOTICZ_URL = 'http://domoticz/json.htm'
OUTDOOR_THERMO_ID = "452"
INDOOR_THERMO_ID = "659"

# Font definitions

ICON_FONT_FILE = os.path.dirname(sys.argv[0]) + "/fonts/Font-Awesome-5-Free-Solid-900.otf"
TEXT_FONT_FILE = os.path.dirname(sys.argv[0]) + "/fonts/NotoSansJP-Regular.otf"

ICON_FONT = ImageFont.truetype(ICON_FONT_FILE, 62)
ICON_FONT_HUGE = ImageFont.truetype(ICON_FONT_FILE, 448)

TEXT_FONT_22 = ImageFont.truetype(TEXT_FONT_FILE, 22)
TEXT_FONT_36 = ImageFont.truetype(TEXT_FONT_FILE, 36)
TEXT_FONT_50 = ImageFont.truetype(TEXT_FONT_FILE, 50)
TEXT_FONT_62 = ImageFont.truetype(TEXT_FONT_FILE, 62)

# Pre-drawn background and top layer images

BASE_IMAGE = os.path.dirname(sys.argv[0]) + "/images/weather-infocentre-background.png"
OVERLAY_IMAGE = os.path.dirname(sys.argv[0]) + "/images/weather-infocentre-overlay.png"

# Known positions and custom colours of calculated text element

IN_TEMP_POS = (82, 6)
OUT_TEMP_POS = (82, 64)
IN_HUM_POS = (245,6)
OUT_HUM_POS = (245, 64)
WEATHER_POS = (15, 168)
EXCHANGERATE_POS = (15, 350)
JPY_ARROW_POS = (556, 368)
GBP_ARROW_POS = (556, 406)
HUGE_WEATHER_COLOUR = (190, 190, 255)

PALETTE = [
    (0, 0, 0),
    (255, 255, 255),
    (0, 255, 0),
    (0, 0, 255),
    (255, 0, 0),
    (255, 255, 0),
    (255, 140, 0),
    (255, 255, 255)
]

SATURATION = 1.0

# Script run time

TIMENOW = str(datetime.now().time()).split(".")[0]

# https://www.metoffice.gov.uk/datapoint/support/documentation/code-definitions
# This page defines the weather codes from 0-30, so it makes sense to me to create
# a list of dictionaries to store the text with its width and height. The weather
# code corresponds to the weather type, W, returned by the API.
WEATHERTYPE = buildWeatherTypes()

# Varables and devices

inky = Inky()
image = Image.new("RGBA", (inky.WIDTH, inky.HEIGHT), PALETTE[inky.WHITE])
overlay = Image.open(OVERLAY_IMAGE)
draw = ImageDraw.Draw(image)
os.chdir(os.path.dirname(sys.argv[0]))



########## The code itself

if __name__ == "__main__":
  try:
    inTemp, inHumidity = getIndoorTempData()
    outTemp, outHumidity = getOutdoorTempData()

    # Get the data and whittle it down to the first four
    try:
      weatherData = parseWeather(requests.get(DATAPOINT_URL).json()['SiteRep']['DV']['Location']['Period'])
    except:
      weatherData = "????"

    weatherString = ""
    for entry in weatherData:
      weatherString += WEATHERTYPE[int(entry['W'])]['text']

    with open(os.path.dirname(sys.argv[0]) + '/exchangerate.txt', "r") as f:
      RATE = f.read()

    BACKGROUND_WEATHER = weatherString[0]

    IN_TEMP_TEXT = inTemp + '°C'
    IN_HUM_TEXT = inHumidity + '%'
    OUT_TEMP_TEXT = outTemp + '°C'
    OUT_HUM_TEXT = outHumidity + '%'

    # Some sizes need calculating
    HUGE_WEATHER_SIZE_X, HUGE_WEATHER_SIZE_Y = ICON_FONT_HUGE.getsize(BACKGROUND_WEATHER)
    HUGE_WEATHER_POS = ((inky.WIDTH-HUGE_WEATHER_SIZE_X)/2, (inky.HEIGHT-HUGE_WEATHER_SIZE_Y)/2)
    TIMENOW_SIZE_X, TIMENOW_SIZE_Y = TEXT_FONT_22.getsize(TIMENOW)
    TIMENOW_POS = (inky.WIDTH - 1 - 1 - TIMENOW_SIZE_X, 1)

    draw.text(HUGE_WEATHER_POS, BACKGROUND_WEATHER, HUGE_WEATHER_COLOUR, ICON_FONT_HUGE)
    draw.text(TIMENOW_POS, TIMENOW, PALETTE[inky.BLUE], TEXT_FONT_22)
    draw.text(IN_TEMP_POS, IN_TEMP_TEXT, PALETTE[inky.BLACK], TEXT_FONT_50)
    draw.text(OUT_TEMP_POS, OUT_TEMP_TEXT, PALETTE[inky.BLACK], TEXT_FONT_50)
    draw.text(IN_HUM_POS, IN_HUM_TEXT, PALETTE[inky.BLACK], TEXT_FONT_36)
    draw.text(OUT_HUM_POS, OUT_HUM_TEXT, PALETTE[inky.BLACK], TEXT_FONT_36)
    draw.text(WEATHER_POS, weatherString, PALETTE[inky.RED], ICON_FONT)
    draw.text(EXCHANGERATE_POS, "\u00A5" + str(round(float(RATE), 3)) + " to £1", PALETTE[inky.BLUE], TEXT_FONT_62)
    draw.text(TIMENOW_POS, TIMENOW, PALETTE[inky.BLUE], TEXT_FONT_22)

    image.alpha_composite(overlay)
    inky.set_image(image, SATURATION)
    inky.show()

  except requests.exceptions.RequestException as err:
    print(err)
    sys.exit(1)
