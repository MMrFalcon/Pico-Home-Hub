
import json
from time import sleep
import switches
import request as http
import wifi
import DS18B20
from request import ResponseType, HttpRequest
import gc

# Redirect print output to a log file. Created for debugging in development mode only.
def log_print(*args, **kwargs):
    with open("log.txt", "a") as log_file: 
        print(*args, **kwargs, file=log_file)
        print(*args, **kwargs)


# Available types: 1 - JSON, 2 - HTML
response_type_header = "X-RESPONSE-TYPE:"

# TODO read html with javascript from other file
def webpage():
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./lighton" method="POST">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <div class="switches-state">
            {switches.reportSwitchState()}
            </div>
            </body>
            </html>
            """
    return str(html)

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
            elif httpRequest.endpoint =='/switch-one/on':
                switches.switchOneOn()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint =='/switch-one/off':
                switches.switchOneOff()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint =='/switch-two/on':
                switches.switchTwoOn()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint =='/switch-two/off':
                switches.switchTwoOff()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint =='/switch-three/on':
                switches.switchThreeOn()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint =='/switch-three/off':
                switches.switchThreeOff()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint =='/switch-four/on':
                switches.switchFourOn()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint =='/switch-four/off':
                switches.switchFourOff()
                response = switches.reportSwitchState()
            elif httpRequest.endpoint =='/switch-report':
                response = switches.reportSwitchState()
            elif httpRequest.endpoint == '/read-temp':
                sensorLib = DS18B20.DS18B20(22)
                temp = sensorLib.redTemp()
                tempObj = {
                    "temp": temp,
                }
                response = json.dumps(tempObj)
            else:
                pass

            client.send("HTTP/1.1 200 OK\r\n")
  
            if (httpRequest.responseType == ResponseType.HTML):
                response = webpage()
                client.send("Content-Type: text/html\r\n")
            else:
                client.send("Content-Type: application/json\r\n")

            client.send("Content-Length: {}\r\n".format(len(response)))
            client.send("\r\n")
            client.send(response)
            client.close()

        except OSError as e:
            print("OS error cached, it should be a timeout, for doing other stuffs between client requests: {}".format(e))
            # sensorLib = DS18B20.DS18B20(22)
            # temp = sensorLib.redTemp()
            # print("Send it or store in array, when client ask for it send it " + temp)
            pass

        wifiConnection.checkConnection()

# Main program starts here
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