"""
API:
Enable screen.
Enabled by default. If connect was lost (for example wiring issue) try to establish connection:
http://192.168.0.13:80/enable-screen
Returns: 
{
	"available": true
}

Disable screen (save energy when on battery)
http://192.168.0.13:80/disable-screen
Returns: 
{
	"available": false
}

Read temp from DS18B20 in Celsius degrees
http://192.168.0.13:80/read-temp
Returns:
{
	"temp": "23.50"
}
"""

import json
from time import sleep
from screen_hd44780 import Hd44780
import switches
import request as http
import wifi
import DS18B20
from request import HttpRequest
import gc
from machine import Pin, I2C
import sys


def serve(wifiConnection: wifi.Wifi):
    while True:
        print("Waiting for client connections...")
        # connection is an opened socket. Accept method returns tuple: conn which is(new socket[0]) and address 
        # socket is blocking main thread, waiting for client connection.
        # Library adds socketOpened.settimeout(5.0) to interrupt blocked thread and do other stuffs like
        # check wifi connection.
        try:   
            wifiConnection.socketOpened.settimeout(5.0)
            client = wifiConnection.socketOpened.accept()[0]
            print(client)
            # Receive data from the socket as byte object max 1024 bytes.
            requestBytes = client.recv(1024)
            requestString = str(requestBytes)
            print(requestString)
            httpRequest: HttpRequest = http.HttpRequest(requestString)
            print("Parsed request: {}".format(httpRequest))
            response = ''

            if httpRequest.endpoint == '/lighton?':
                switches.ledOn()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint =='/lightoff?':
                switches.ledOff()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint == '/read-temp':
                sensorLib = DS18B20.DS18B20(22)
                temp = sensorLib.redTemp()
                tempObj = {
                    "temp": temp,
                }
                response = json.dumps(tempObj)
            # TODO not working in sequence disable -> enable.
            elif httpRequest.endpoint =='/enable-screen':
                global lcd
                lcd = prepareLcd()
                response = json.dumps({"available": lcd.isAvailable()})
            elif httpRequest.endpoint =='/disable-screen':
                print("Request for disable screen")
                global lcd
                lcd.turnOff()
                response = json.dumps({"available": "false"})
            else:
                pass

            client.send("HTTP/1.1 200 OK\r\n")
            client.send("Content-Type: json\r\n")
            client.send("Content-Length: {}\r\n".format(len(response)))
            client.send("\r\n")
            client.send(response)
            client.close()

        except OSError as e:
            print("OS error cached, it should be a timeout, for doing other stuffs between client requests: {}".format(e))
            sensorLib = DS18B20.DS18B20(22)
            temp = sensorLib.redTemp()
            showTemp(temp)
            # print("Send it or store in array, when client ask for it send it " + temp)
            pass

        except Exception as unhandledError:
            print("Unexpected error:", unhandledError)
            sys.print_exception(unhandledError)
            pass

        wifiConnection.checkConnection()

def showTemp(temp: str):
    try:
        global lcd
        lcd.clear()
        lcd.home()
        lcd.write("Temp: " + temp)
    except Exception as unhandledError:
        print("Unexpected error:", unhandledError)
        pass


def prepareLcd():
    try:
        sda = Pin(0)
        scl = Pin(1)
        i2c = I2C(0,sda=sda,scl=scl, freq=400000)
        print(i2c.scan())
        I2C_ADDR     = 39
        I2C_NUM_ROWS = 2
        I2C_NUM_COLS = 16
        lcdForReturn = Hd44780(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
        return lcdForReturn
    except Exception as unhandledError:
        print("Unexpected error:", unhandledError)
        pass

# Main program starts here
lcd = prepareLcd()
try:
    print("Starting app...")
    gc.collect()
    sleep(3)
    wifiConnection: wifi.Wifi = wifi.Wifi()
    serve(wifiConnection)
except KeyboardInterrupt:
    print("KeyboardInterrupt")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    wifiConnection.socketOpened.close()