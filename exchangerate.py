#!/usr/bin/python3

import requests, os, sys
import exchangeratekey_bb as exchangeratekey

FILENAME = os.path.dirname(sys.argv[0]) + '/exchangerate.txt'
RESPONSEDATA = requests.get("https://openexchangerates.org/api/latest.json", params={'symbols': 'GBP,EUR,JPY', 'app_id': exchangeratekey.APIKEY}).json()
rate = RESPONSEDATA['rates']['JPY'] / RESPONSEDATA['rates']['GBP']
with open(FILENAME, "w") as f:
    f.write(str(rate))
