import inkyphat, requests, sys, wundergroundkey
from PIL import ImageFont

WUNDERGROUND_URL = "http://api.wunderground.com/api/" + wundergroundkey.APIKEY + "/hourly/q/" + wundergroundkey.LOCATION + ".json"

OUTDOOR_THERMO_ID = "80"
INDOOR_THERMO_ID = "4"

SMALL_FONT = ImageFont.truetype(inkyphat.fonts.FredokaOne, 14)
LARGE_FONT = ImageFont.truetype(inkyphat.fonts.FredokaOne, 36)
WEATHER_FONT = ImageFont.truetype("FA5FreeSolid900.otf", 20)

IN_TEXT = "In"
IN_TEXT_W, IN_TEXT_H = SMALL_FONT.getsize(IN_TEXT)
OUT_TEXT = "Out"
OUT_TEXT_W, OUT_TEXT_H = SMALL_FONT.getsize(OUT_TEXT)
SUN_TEXT = "\uF185"
SUN_TEXT_W, SUN_TEXT_H = WEATHER_FONT.getsize(SUN_TEXT)
MOON_TEXT = "\uF186"
MOON_TEXT_W, MOON_TEXT_H = WEATHER_FONT.getsize(MOON_TEXT)
CLOUD_TEXT = "\uF0C2"
CLOUD_TEXT_W, CLOUD_TEXT_H = WEATHER_FONT.getsize(CLOUD_TEXT)
LGHT_TEXT = "\uF0E7"
LGHT_TEXT_W, LGHT_TEXT_H = WEATHER_FONT.getsize(LGHT_TEXT)
RAIN_TEXT = "\uF0E9"
RAIN_TEXT_W, RAIN_TEXT_H = WEATHER_FONT.getsize(RAIN_TEXT)
SNOW_TEXT = "\uF2DC"
SNOW_TEXT_W, SNOW_TEXT_H = WEATHER_FONT.getsize(SNOW_TEXT)

#Corresponds to all WeatherUnderground icon names
SUN_LIST = ['clear', 'mostlysunny', 'partlycloudy', 'partlysunny', 'sunny']
CLOUDY_LIST = ['mostlycloudy', 'cloudy', 'fog', 'hazy']
THUNDER_LIST = ['chancetstorms', 'tstorms', 'unknown']
RAIN_LIST = ['chancerain', 'rain']
SNOW_LIST = ['chanceflurries', 'chancesleet', 'chancesnow', 'flurries', 'sleet', 'snow']

try:
  inkyphat.rectangle([(0,0),(211,103)],inkyphat.WHITE)
  inkyphat.set_border(inkyphat.RED)

  inData = requests.get('http://domoticz/json.htm?type=devices&rid=' + INDOOR_THERMO_ID).json()['result'][0]
  outData = requests.get('http://domoticz/json.htm?type=devices&rid=' + OUTDOOR_THERMO_ID).json()['result'][0]
  weatherData = requests.get(WUNDERGROUND_URL)

  inkyphat.text((3,3), IN_TEXT, inkyphat.BLACK, SMALL_FONT)
  inkyphat.text((3 + OUT_TEXT_W + 3, 3), str(inData['Temp']) + '°C', inkyphat.BLACK, LARGE_FONT)
  inkyphat.text((3, 3 + LARGE_FONT.getsize(str(inData['Temp']))[1] + 3), OUT_TEXT, inkyphat.BLACK, SMALL_FONT)
  inkyphat.text((3 + OUT_TEXT_W + 3, 3 + LARGE_FONT.getsize(str(inData['Temp']))[1] + 3), str(outData['Temp']) + '°C', inkyphat.BLACK, LARGE_FONT)

  weatherString = ""
  # [0:11:2] slices the weather forecast into every other hour for the next twelve hours (i.e. 6 icons)
  for hourlyWeatherData in weatherData.json()['hourly_forecast'][0:11:2]:
    if hourlyWeatherData['icon'] in SUN_LIST:
      if int(hourlyWeatherData['FCTTIME']['hour']) < 6 or int(hourlyWeatherData['FCTTIME']['hour']) >= 18:
        weatherString += MOON_TEXT
      else:
        weatherString += SUN_TEXT
    elif hourlyWeatherData['icon'] in CLOUDY_LIST:
      weatherString += CLOUD_TEXT
    elif hourlyWeatherData['icon'] in THUNDER_LIST:
      weatherString += LGHT_TEXT
    elif hourlyWeatherData['icon'] in RAIN_LIST:
      weatherString += RAIN_TEXT
    elif hourlyWeatherData['icon'] in SNOW_LIST:
      weatherString += SNOW_TEXT

  WTH_TEXT_W, WTH_TEXT_H = WEATHER_FONT.getsize(weatherString)
  inkyphat.text((3, 103 - WTH_TEXT_H - 3), weatherString, inkyphat.RED, WEATHER_FONT)

  inkyphat.show()

except requests.exceptions.RequestException as err:
  print(err)
  sys.exit(1)

