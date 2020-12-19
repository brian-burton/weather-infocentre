import inkyphat, requests, sys, metofficekey
from PIL import ImageFont
from datetime import datetime

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

##### Constants #####

DATAPOINT_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/" + metofficekey.LOCATION + "?res=3hourly&key=" + metofficekey.APIKEY
DOMOTICZ_URL = 'http://domoticz/json.htm'

OUTDOOR_THERMO_ID = "452"
INDOOR_THERMO_ID = "223"

SMALL_FONT = ImageFont.truetype(inkyphat.fonts.FredokaOne, 14)
MED_FONT = ImageFont.truetype(inkyphat.fonts.FredokaOne, 28)
LARGE_FONT = ImageFont.truetype(inkyphat.fonts.FredokaOne, 35)
WEATHER_FONT = ImageFont.truetype("Font Awesome 5 Free-Solid-900.otf", 20)

IN_TEXT = "In"
IN_TEXT_W, IN_TEXT_H = SMALL_FONT.getsize(IN_TEXT)
OUT_TEXT = "Out"
OUT_TEXT_W, OUT_TEXT_H = SMALL_FONT.getsize(OUT_TEXT)

HOUR_IN_MINS = datetime.now().hour * 60


# https://www.metoffice.gov.uk/datapoint/support/documentation/code-definitions
# This page defines the weather codes from 0-30, so it makes sense to me to create
# a list of dictionaries to store the text with its width and height. The weather
# code corresponds to the weather type, W, returned by the API.
WEATHERTYPE = buildWeatherTypes()

try:
  maxWidth = 0
  inkyphat.rectangle([(0,0),(211,103)],inkyphat.WHITE)
  inkyphat.set_border(inkyphat.RED)

  try:
    inData = requests.get(DOMOTICZ_URL + '?type=devices&rid=' + INDOOR_THERMO_ID).json()['result'][0]
    inTemp = str(inData['Temp'])
    inHumidity = str(inData['Humidity'])
  except:
    inTemp = "?.?"
    inHumidity = "?"

  try:
    outData = requests.get(DOMOTICZ_URL + '?type=devices&rid=' + OUTDOOR_THERMO_ID).json()['result'][0]
    outTemp = str(outData['Temp'])
    outHumidity = str(outData['Humidity'])
  except:
    outTemp = "?.?"
    outHumidity = "?"

  IN_TEMP_TEXT = inTemp + '°C'
  IN_TEMP_TEXT_W, IN_TEMP_TEXT_H = LARGE_FONT.getsize(IN_TEMP_TEXT)
  IN_HUM_TEXT = inHumidity + '%'
  IN_HUM_TEXT_W, IN_HUM_TEXT_H = MED_FONT.getsize(IN_HUM_TEXT)
  OUT_TEMP_TEXT = outTemp + '°C'
  OUT_TEMP_TEXT_W, OUT_TEMP_TEXT_H = LARGE_FONT.getsize(OUT_TEMP_TEXT)
  OUT_HUM_TEXT = outHumidity + '%'
  OUT_HUM_TEXT_W, OUT_HUM_TEXT_H = MED_FONT.getsize(OUT_HUM_TEXT)

  # Get the data and whittle it down to the first four
  try:
    weatherData = parseWeather(requests.get(DATAPOINT_URL).json()['SiteRep']['DV']['Location']['Period'])
  except:
    weatherData = "????"

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

  inkyphat.text((in_text_x,in_text_y), IN_TEXT, inkyphat.BLACK, SMALL_FONT)
  inkyphat.text((temp_text_x, in_temp_text_y), IN_TEMP_TEXT, inkyphat.BLACK, LARGE_FONT)
  inkyphat.text((out_text_x, out_text_y), OUT_TEXT, inkyphat.BLACK, SMALL_FONT)
  inkyphat.text((temp_text_x, out_text_y), OUT_TEMP_TEXT, inkyphat.BLACK, LARGE_FONT)
  inkyphat.text((hum_text_x, in_text_y), IN_HUM_TEXT, inkyphat.BLACK, MED_FONT)
  inkyphat.text((hum_text_x, out_text_y), OUT_HUM_TEXT, inkyphat.BLACK, MED_FONT)
  weatherString = ""
  for entry in weatherData:
    weatherString += WEATHERTYPE[int(entry['W'])]['text']
  WTH_TEXT_W, WTH_TEXT_H = WEATHER_FONT.getsize(weatherString)
  inkyphat.text((3, 103 - WTH_TEXT_H - 3), weatherString, inkyphat.RED, WEATHER_FONT)

  inkyphat.show()

except requests.exceptions.RequestException as err:
  print(err)
  sys.exit(1)

