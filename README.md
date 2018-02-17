# Home Weather Info Centre

## Purpose

This code provides a basic heads-up display for my wife in our bedroom.

Based on a [Raspberry Pi Zero](https://www.raspberrypi.org/) with a [Pimoroni Inky pHat](https://shop.pimoroni.com/products/inky-phat), it reads indoor and outdoor temperature readings from a [Domoticz](http://domoticz.com/) server in my house and weather for the next 12 hours from the [Weather Underground API](https://www.wunderground.com/weather/api).

## Prerequisites

You'll need:

- A Raspberry Pi, kept up to date with Raspbian Squeeze
- A [Pimoroni Inky pHat](https://shop.pimoroni.com/products/inky-phat) with [libraries](https://github.com/pimoroni/inky-phat)
- Python 3, with requests (```sudo pip3 install requests```)
- The [Font Awesome 5](https://fontawesome.com/) solid otf file for the weather icons

## Setup

Setup is simple. Just ```git clone``` this repo, edit ```wundergroundkey.py``` to add your location and API key and then just ```python3 infocentre.py```. I use a simple cron job to run at boot and periodically while we're awake.

Weather Underground have a generous free tier for this kind of thing, but just be aware how often you are updating. Realistically the weather doesn't change radically every hour, but the script updates temperature and weather at the same time.