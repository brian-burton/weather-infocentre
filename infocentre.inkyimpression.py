#!/usr/bin/python3

import requests
import sys
import os
import metofficekey_bb as metofficekey
from inky.auto import auto
from font_fredoka_one import FredokaOne
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from time import sleep

# Varables and devices

inky = auto()
xres, yres = inky.resolution
image = Image.new("P", inky.resolution)
draw = ImageDraw.Draw(image)
os.chdir(os.path.dirname(sys.argv[0]))


##### Function defs #####

def parseWeather(data: list) -> list:
  """ take MetOffice weatherdata and return the first four future entries"""
  forecast = []
  whichday = 0
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
    tmp['w'], tmp['h'] = WEATHER_FONT.getsize(text)
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

SMALL_FONT = ImageFont.truetype(FredokaOne, 14)
MED_FONT = ImageFont.truetype(FredokaOne, 28)
LARGE_FONT = ImageFont.truetype(FredokaOne, 35)
WEATHER_FONT = ImageFont.truetype("Font-Awesome-5-Free-Solid-900.otf", 20)

IN_TEXT = "In"
IN_TEXT_W, IN_TEXT_H = SMALL_FONT.getsize(IN_TEXT)
OUT_TEXT = "Out"
OUT_TEXT_W, OUT_TEXT_H = SMALL_FONT.getsize(OUT_TEXT)

HOUR_IN_MINS = datetime.now().hour * 60
TIMENOW = str(datetime.now().time()).split(".")[0]
TIMENOW_W, TIMENOW_H = SMALL_FONT.getsize(TIMENOW)

# https://www.metoffice.gov.uk/datapoint/support/documentation/code-definitions
# This page defines the weather codes from 0-30, so it makes sense to me to create
# a list of dictionaries to store the text with its width and height. The weather
# code corresponds to the weather type, W, returned by the API.
WEATHERTYPE = buildWeatherTypes()


########## The code itself

if __name__ == "__main__":
  try:
    draw.rectangle([(0,0),(xres-1,yres-1)],fill=inky.WHITE)
    draw.rectangle([(1,1),(xres-2,yres-2)],outline=inky.RED)
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

    IN_TEMP_TEXT = inTemp + '°C'
    IN_TEMP_TEXT_W, IN_TEMP_TEXT_H = LARGE_FONT.getsize(IN_TEMP_TEXT)
    IN_HUM_TEXT = inHumidity + '%'
    IN_HUM_TEXT_W, IN_HUM_TEXT_H = MED_FONT.getsize(IN_HUM_TEXT)
    OUT_TEMP_TEXT = outTemp + '°C'
    OUT_TEMP_TEXT_W, OUT_TEMP_TEXT_H = LARGE_FONT.getsize(OUT_TEMP_TEXT)
    OUT_HUM_TEXT = outHumidity + '%'
    OUT_HUM_TEXT_W, OUT_HUM_TEXT_H = MED_FONT.getsize(OUT_HUM_TEXT)
    WTH_TEXT_W, WTH_TEXT_H = WEATHER_FONT.getsize(weatherString)


    in_out_w_max = max(IN_TEXT_W, OUT_TEXT_W)
    temp_w_max = max(IN_TEMP_TEXT_W, OUT_TEMP_TEXT_W)
    hum_w_max = max(IN_HUM_TEXT_W, OUT_HUM_TEXT_W)
    in_text_x = 3
    in_text_y = 3
    temp_text_x = in_text_x + in_out_w_max + 3
    out_text_x = 3
    out_text_y = 3 + IN_TEMP_TEXT_H + 3
    in_temp_text_y = 3
    out_temp_text_y = out_text_y
    hum_text_x = 211 - hum_w_max - 3
    out_hum_text_y = 3
    wth_text_x = 3
    wth_text_y = out_text_y + OUT_TEMP_TEXT_H + 3
    rate_text_x = 3
    rate_text_y = wth_text_y + WTH_TEXT_H + 3
    time_text_x = xres - 1 - 3 - TIMENOW_W
    time_text_y = 3

    draw.text((in_text_x,in_text_y), IN_TEXT, inky.BLACK, SMALL_FONT)
    draw.text((temp_text_x, in_temp_text_y), IN_TEMP_TEXT, inky.BLACK, LARGE_FONT)
    draw.text((out_text_x, out_text_y), OUT_TEXT, inky.BLACK, SMALL_FONT)
    draw.text((temp_text_x, out_text_y), OUT_TEMP_TEXT, inky.BLACK, LARGE_FONT)
    draw.text((hum_text_x, in_text_y), IN_HUM_TEXT, inky.BLACK, MED_FONT)
    draw.text((hum_text_x, out_text_y), OUT_HUM_TEXT, inky.BLACK, MED_FONT)
    draw.text((wth_text_x, wth_text_y), weatherString, inky.RED, WEATHER_FONT)
    draw.text((rate_text_x, rate_text_y), "\u00A5" + str(round(float(RATE), 3)) + " to £1", inky.BLACK, LARGE_FONT)
    draw.text((time_text_x, time_text_y), TIMENOW, inky.BLUE, SMALL_FONT)

    inky.set_image(image)
    inky.show()

  except requests.exceptions.RequestException as err:
    print(err)
    sys.exit(1)
