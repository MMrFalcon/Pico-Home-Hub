
import network
import config
import socket
from time import sleep

ssid = config.WIFI_SSID
password = config.WIFI_PASSWORD
wifiCheckSleepTimeSec = 5

class Wifi:
    wlan: network.WLAN = None
    ip: str = None
    socketOpened: socket = None

    def __init__(self):
        self.ip = self.connect()
        if not self.ip == None:
            statusCode = -1
            tryCount = 0
            while (statusCode != 0 and tryCount < 10):
                print("Status code for opening socket: {}, tryCount: {}".format(statusCode, tryCount))
                tryCount = tryCount + 1
                statusCode = self.openSocket()

    
    def connect(self):
        # connect as client. AP_IF - make access point
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.ifconfig((config.IP_ADDRESS, config.SUBNET_MASK, config.GATEWAY, config.DNS))
        self.wlan.connect(ssid, password)
        connectionAttemps = 0
        while self.wlan.isconnected() == False:
            print('Waiting for connection...')
            sleep(1)
            connectionAttemps = connectionAttemps + 1
            print("Connection attemps: {}".format(connectionAttemps))
            if (connectionAttemps == 5):
                raise Exception("Maximum connection attemps reached")
        print(self.wlan.ifconfig())
        return self.wlan.ifconfig()[0]

    def openSocket(self) -> int:
        try:
            print("Try to open socket")
            address = (self.ip, 80)
            self.socketOpened = socket.socket()
            self.socketOpened.bind(address)
            self.socketOpened.listen(1)
            print(self.socketOpened)
            return 0
        except OSError as e:
            # address in use
            print("OS error catched...")
            if e.errno == 98:
                print("Handling address in use")
                # soft reset for now
                self.socketOpened.close()
                sleep(5) 
                return -1


    def reconnect(self):
        print("Request for reconnect to WiFi network")
        self.wlan.disconnect() 
        self.connect()
        print(self.wlan.ifconfig())
        self.ip = self.wlan.ifconfig()[0]
        self.openSocket()

    def checkConnection(self):
        while True:
            print("Checking Wifi connection...")
            if self.wlan.isconnected():
                print("WiFi connected...")
            else:
                print("Wifi not connected...")
                self.reconnect()
            sleep(wifiCheckSleepTimeSec)
