# Home Weather Info Centre

## Purpose

This code provides a basic heads-up display for my wife in our bedroom.

Based on a [Raspberry Pi Zero](https://www.raspberrypi.org/) with a [Pimoroni Inky pHat](https://shop.pimoroni.com/products/inky-phat), it reads indoor and outdoor temperature readings from a [Domoticz](http://domoticz.com/) server in my house and weather for the next 12 hours from the [Met Office Datapoint API](https://www.metoffice.gov.uk/services/data).

## Prerequisites

I use:

- A Raspberry Pi, kept up to date with Raspberry Pi OS
- A [Pimoroni Inky pHat](https://shop.pimoroni.com/products/inky-phat) with [libraries](https://github.com/pimoroni/inky)
- Python 3, with requests (```sudo pip3 install requests```)
- The [Font Awesome](https://fontawesome.com/how-to-use/on-the-desktop/setup/getting-started) solid otf file for the weather icons
- Calls to the [Domoticz API](https://www.domoticz.com/wiki/Domoticz_API/JSON_URL%27s) (my home automation platform) for temperature inside and outside the house.

## Setup

Setup is simple. Just ```git clone``` this repo, edit ```metofficekey.py``` to add your location and API key and then just ```python3 infocentre.metoffice.py```. I use a simple cron job to run at boot and periodically while we're awake.

Met Office have a decent [fair use policy](https://www.metoffice.gov.uk/about-us/legal/fair-usage), but just be aware how often you are updating. Realistically the weather doesn't change radically every hour, but the script updates temperature and weather at the same time.
