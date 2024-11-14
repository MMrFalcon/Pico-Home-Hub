import network
import socket
from time import sleep
import machine
import _thread
import switches
import config
import request as http
import wifi
from request import ResponseType, RequestMethod, HttpRequest

# Available types: 1 - JSON, 2 - HTML
response_type_header = "X-REPONSE-TYPE:"

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
            elif httpRequest.endpoint =='/lightoff?':
                switches.ledOff()
            elif httpRequest.endpoint =='/switch-one/on':
                switches.switchOneOn()
            elif httpRequest.endpoint =='/switch-one/off':
                switches.switchOneOff()
            elif httpRequest.endpoint =='/switch-two/on':
                switches.switchTwoOn()
            elif httpRequest.endpoint =='/switch-two/off':
                switches.switchTwoOff()
            elif httpRequest.endpoint =='/switch-three/on':
                switches.switchThreeOn()
            elif httpRequest.endpoint =='/switch-three/off':
                switches.switchThreeOff()
            elif httpRequest.endpoint =='/switch-report':
                pass

            response = switches.reportSwitchState()

            client.send("HTTP/1.1 200 OK\r\n")
            if (httpRequest.responseType == ResponseType.HTML):
                response = webpage()
                client.send("Content-Type: text/html\r\n")
            else:
                client.send("Content-Type: json\r\n")

            client.send("Content-Length: {}\r\n".format(len(response)))
            client.send("\r\n")
            client.send(response)
            client.close()
        except OSError as e:
            print("OS error catched {}".format(e))
            pass

        checkWifiConnection(wifiConnection)

def checkWifiConnection(wifiConnection: wifi.Wifi):
    try:
        if wifiConnection.wlan.isconnected():
            print("Wifi connected...")
        else:
            print("Wifi connection lost...")
            wifiConnection.reconnect()
    except Exception as e:
        print("Connection error: {}".format(e))    
        checkWifiConnection(wifiConnection)
        

def checkWiFiConnectionInNewThread(wifiConnection: wifi.Wifi):
        print("Check wifi in new thread")
        wifiConnection.checkConnection()

# Main program starts here
try:
    # TODO add gc.collect() ?
    wifiConnection: wifi.Wifi = wifi.Wifi()
    # print("Starting new thread job")
    # threadIdentifier = _thread.start_new_thread(checkWiFiConnectionInNewThread, (wifiConnection,))
    # print("Thread identifier: {}".format(threadIdentifier))
    serve(wifiConnection)
except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    wifiConnection.socketOpened.close()