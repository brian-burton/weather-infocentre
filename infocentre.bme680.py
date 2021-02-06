#!/usr/bin/env python
import syslog
import signal
import bme680
import sys
from paho.mqtt import client as mqtt_client
from time import sleep
from threading import Event

sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
exit = Event()

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)

# MQTT Setup

broker = 'mqtt.yayoi.co.uk'
port = 1883
topic = "domoticz/in"
client_id = 'weatherpi'

# Domoticz sensor setup

TempIDX = "659"
BaroIDX = "656"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            syslog.syslog("BME680 connected to MQTT Broker!")
        else:
            syslog.syslog(f"BME680 failed to connect tp MQTTbroker, return code {rc}")
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def termHandler(signal, frame):
    syslog.syslog("Received SIGTERM")
    exit.set()

def main():
    try:
        mqttclient = connect_mqtt()
        signal.signal(signal.SIGTERM,termHandler)
        mqttclient.loop_start()
        while not exit.is_set():
            if sensor.get_sensor_data():
                baro_stat = 0
                if (30 <= sensor.data.humidity <= 70) and (20 <= sensor.data.temperature <= 26):
                    hum_stat = 1
                elif sensor.data.humidity > 70:
                    hum_stat = 3
                elif sensor.data.humidity < 30:
                    hum_stat = 2
                else:
                    hum_stat=0
                mqttclient.publish(topic, f"{{ \"idx\": {TempIDX}, \"command\": \"udevice\", \"nvalue\": 0, \"svalue\": \"{sensor.data.temperature};{sensor.data.humidity};{hum_stat}\" }}")
                mqttclient.publish(topic, f"{{ \"idx\": {BaroIDX}, \"command\": \"udevice\", \"nvalue\": 0, \"svalue\": \"{sensor.data.pressure};{baro_stat}\" }}")
            exit.wait(300)

        syslog.syslog("Terminating cleanly")
        mqttclient.loop_stop()
        mqttclient.disconnect()
        sys.exit(0)

    except Exception as E:
        syslog.syslog(f"BME680 error: {E}")
        mqttclient.loop_stop()
        mqttclient.disconnect()
        sys.exit(1)

if __name__ == "__main__":
    main()
