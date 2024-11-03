import network
import socket
from time import sleep
import machine
import switches
import config

ssid = config.WIFI_SSID
password = config.WIFI_PASSWORD
# Available types: 1 - JSON, 2 - HTML
response_type_header = "X-REPONSE-TYPE:"

class ResponseType():
    class _JSON:
        value = '1'
        def __str__(self):
            return "JSON"
        
        def getValue(self):
            return self.value
        
    class _HTML:
        value = '2'
        def __str__(self):
            return "HTML"
        
        def getValue(self):
            return self.value

    JSON = _JSON()
    HTML = _HTML()

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

def getResponseType(request: str) -> ResponseType: 
    try:
        headerStart = request.find(response_type_header)
        if headerStart == -1:
            print("Header not found; defaulting to HTML.")
            return ResponseType.HTML
        
        headerValue = request[headerStart + len(response_type_header):].split("\r\n", 1)[0].strip()
        print(f"Extracted response type header: '{headerValue}'")

        if headerValue.startswith(ResponseType.JSON.getValue()):
            return ResponseType.JSON
        else:
            return ResponseType.HTML

    except IndexError as e:
        print("Error parsing the response type header, defaulting to HTML.", e)
        return ResponseType.HTML
    
    except Exception as e:
        print("An unexpected error occurred. Getting default response type.", e)
        return ResponseType.HTML


def serve(connection):
    switches.ledOff()
    while True:
        # connection is a opened socket. Accept returns tuple: conn (new socket[0]), address 
        client = connection.accept()[0]
        print(client)
        # Receive data from the socket as byte object max 1024 bytes.
        request = client.recv(1024)
        request = str(request)
        print(request)
        responseType: ResponseType = getResponseType(request)
        print("Response Type: {}".format(responseType))
        response = ''
        try:
            # b'GET /lighton? - will split by first space. [0] = ''GET '
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            switches.ledOn()
        elif request =='/lightoff?':
            switches.ledOff()
        elif request =='/switch-one/on':
            switches.switchOneOn()
            response = switches.reportSwitchState()
            print(response)
        elif request =='/switch-one/off':
            switches.switchOneOff()
            response = switches.reportSwitchState()
            print(response)
        print(request)
        if (responseType == ResponseType.HTML):
            html = webpage()
            client.send("HTTP/1.1 200 OK\r\n")
            client.send("Content-Type: text/html\r\n")
            client.send("Content-Length: {}\r\n".format(len(html)))
            client.send("\r\n")
            client.send(html)
        else:
            client.send("HTTP/1.1 200 OK\r\n")
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