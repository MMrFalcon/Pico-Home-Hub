import network
import socket
from time import sleep
import machine
import switches
import config
import request as http
from request import ResponseType, RequestMethod, HttpRequest

ssid = config.WIFI_SSID
password = config.WIFI_PASSWORD
# Available types: 1 - JSON, 2 - HTML
response_type_header = "X-REPONSE-TYPE:"

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.ifconfig((config.IP_ADDRESS, config.SUBNET_MASK, config.GATEWAY, config.DNS))
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(wlan.ifconfig())
    return wlan.ifconfig()[0]

def openSocket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

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

def serve(connection):
    switches.ledOff()
    while True:
        # connection is a opened socket. Accept returns tuple: conn (new socket[0]), address 
        client = connection.accept()[0]
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

try:
    ip = connect()
    connection  = openSocket(ip)
    serve(connection)
    while(1):
        print("Waiting for tasks...")
        sleep(5)
except KeyboardInterrupt:
    machine.reset()