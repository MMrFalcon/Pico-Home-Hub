#!/usr/bin/python3

"""
This script is used as a scheduled cron job on a Linux system to periodically fetch 
temperature data from a Raspberry Pi Pico-based device ("pico-home-hub") and send 
the readings to two different smart home systems:

1. JHAS (JSON Home Automation System) - The script sends the temperature reading 
   in JSON format via an HTTP POST request to a local JHAS instance.

2. Domoticz - The script sends the temperature value using an HTTP GET request 
   formatted specifically for the Domoticz API, updating the device with a specified IDX.

The sensor data is retrieved by making an HTTP GET request to the Pico device's 
REST endpoint at `http://192.168.0.13:80/read-temp`. The expected response is a JSON 
object with a `"temp"` field containing the temperature value as a string.

All requests and responses are logged to the console for debugging and monitoring.
"""

import datetime
import requests

# Domoticz server
SERVER="192.168.0.2:8080"
# DHT IDX FOR DOMOTICZ REQUEST
DHTIDX="11"
DATE_TIME_STRING = str(datetime.datetime.now())

def send_data_to_jhas(temp):
       print('sending data to JHAS')
       currentTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
       print(currentTime + " : ", temp)
       body = {
              "sensorName": "Temperatura cieplarnia",
              "unitOfMeasureName": "Celsius",
              "unitOfMeasureShortcut": "C",
              "readingDate": currentTime,
              "value": temp
       }
       r = requests.post('http://localhost:8081/api/sensor-data-bucket', json=body)
       print(r.json())
       print(r.status_code)


def getFromSensor():
    r = requests.get('http://192.168.0.13:80/read-temp')
    jsonResponse = r.json()
    print(jsonResponse)
    return jsonResponse['temp']

def send_data_to_domoticz(temperature_c):
    print("TEMP : " + temperature_c)
    URL = ("http://" + SERVER + "/json.htm?type=command&param=udevice&idx=" +
              DHTIDX + "&nvalue=0&svalue=" + temperature_c)
    print(DATE_TIME_STRING + " : " + "Sending request with url ", URL)

    r = requests.get(url = URL)

    data = r.json()
    print(data)

temp = getFromSensor()
print("Value from JSON " + temp)
send_data_to_jhas(temp)
send_data_to_domoticz(temp)