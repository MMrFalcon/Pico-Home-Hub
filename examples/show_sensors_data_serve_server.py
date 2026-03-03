import lib.DHT22 as DHT22
import lib.sh1106 as sh1106
import lib.oky16560 as oky16560
from time import sleep
from machine import Pin, I2C
import gc
import json
import time

import lib.wifi as wifi
import lib.request as http



sensor = DHT22.DHT_Sensor(0)
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
oled: sh1106.SH1106 = sh1106.SH1106(i2c, 0x3c)
lightSensor = oky16560.Oky16560()

lastDisplayUpdate = 0
DISPLAY_INTERVAL = 30000

def printDataNonBlocking():
    global lastDisplayUpdate

    now = time.ticks_ms()

    if time.ticks_diff(now, lastDisplayUpdate) >= DISPLAY_INTERVAL:
        lastDisplayUpdate = now

        data: DHT22.DHT_Data = sensor.get_data()
        temperature = data.temperature + " (C)"
        humidity = data.humidity + " %"
        lightValue = str(lightSensor.get_light_level())

        oled.printText("Temp: " + temperature, 1, clearScreen=True)
        oled.printText("Hum: " + humidity, 2, clearScreen=False)
        oled.printText("Light: " + lightValue, 3, clearScreen=False)

## Helper Function - print data and freez the thread.
def printData():
    data: DHT22.DHT_Data = sensor.get_data()
    temperature = data.temperature + " (C)"
    humidity = data.humidity + " %"
    lightValue = lightSensor.get_light_level()
    print(lightValue)
    print(temperature)
    print(humidity)
    oled.printText("Temp: " + temperature, 1, clearScreen=True)
    oled.printText("Hum: " + humidity, 2, clearScreen=False)
    oled.printText(lightValue, 3, clearScreen=False)
    sleepTime = 30
    for i in range(sleepTime):
        oled.clear_text_line(oled.frameBuffer, 4)
        oled.printText("Next in: {}s".format(sleepTime - i), 4, clearScreen=False)
        sleep(1)
    # sleep(30)

def reportGrowBoxState():
    data: DHT22.DHT_Data = sensor.get_data()
    temperature = data.temperature + " (C)"
    humidity = data.humidity + " %"
    lightValue = lightSensor.get_light_level()
    growBoxState = {
        "temperature": temperature,
        "humidity": humidity,
        "lightValue": lightValue,
    }
    return json.dumps(growBoxState)


def serve(wifiConnection: wifi.Wifi):
    print("Waiting for client connections...")

    try:
        wifiConnection.socketOpened.settimeout(5.0)
        client = wifiConnection.socketOpened.accept()[0]
        print(client)
        # Receive data from the socket as byte object max 1024 bytes.
        requestBytes = client.recv(1024)
        requestString = str(requestBytes)
        print(requestString)
        httpRequest: http.HttpRequest = http.HttpRequest(requestString)
        print("Parsed request: {}".format(httpRequest))
        response = ''

        if httpRequest.endpoint == '/report':
            response = reportGrowBoxState()
        else:
            pass

        client.send("HTTP/1.1 200 OK\r\n")

        client.send("Content-Type: application/json\r\n")

        client.send("Content-Length: {}\r\n".format(len(response)))
        client.send("\r\n")
        client.send(response)
        client.close()

    except OSError as e:
        print("OS error cached, it should be a timeout, for doing other stuffs between client requests: {}".format(e))
        pass

    wifiConnection.checkConnection()

# while(1):
#     printData()

try:
    print("Starting app...")
    gc.collect()
    time.sleep(3)
    wifiConnection: wifi.Wifi = wifi.Wifi()
    while True:
        serve(wifiConnection)
        printDataNonBlocking()
        time.sleep(0.05)

except KeyboardInterrupt:
    print("KeyboardInterrupt")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    wifiConnection.socketOpened.close()