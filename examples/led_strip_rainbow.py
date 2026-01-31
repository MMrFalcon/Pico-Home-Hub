import time
from lib.WS2812B_argb import WS2812B

print("BOOT OK")

ledStrip = WS2812B(0, 30)

while True:
    ledStrip.rainbow_step()
    time.sleep(0.05)

## API with Wi-Fi
### Enable light
# GET http://192.168.0.16/light-on

### Disable light
# GET http://192.168.0.16/light-off

# import gc
# import json
# import time
# from lib.WS2812B_argb import WS2812B
# import lib.wifi as wifi
# import lib.request as http
#
# print("BOOT OK")
# lightEnabled = False
#
#
# def reportLightState():
#     global lightEnabled
#     switchStates = {
#         "lightEnabled": lightEnabled,
#     }
#     return json.dumps(switchStates)
#
#
# def serve(wifiConnection: wifi.Wifi):
#     global lightEnabled
#     print("Waiting for client connections...")
#
#     try:
#         wifiConnection.socketOpened.settimeout(5.0)
#         client = wifiConnection.socketOpened.accept()[0]
#         print(client)
#         # Receive data from the socket as byte object max 1024 bytes.
#         requestBytes = client.recv(1024)
#         requestString = str(requestBytes)
#         print(requestString)
#         httpRequest: http.HttpRequest = http.HttpRequest(requestString)
#         print("Parsed request: {}".format(httpRequest))
#         response = ''
#
#         if httpRequest.endpoint == '/light-on':
#             lightEnabled = True
#             response = reportLightState()
#         elif httpRequest.endpoint == '/light-off':
#             lightEnabled = False
#             response = reportLightState()
#         else:
#             pass
#
#         client.send("HTTP/1.1 200 OK\r\n")
#
#         client.send("Content-Type: application/json\r\n")
#
#         client.send("Content-Length: {}\r\n".format(len(response)))
#         client.send("\r\n")
#         client.send(response)
#         client.close()
#
#     except OSError as e:
#         print("OS error cached, it should be a timeout, for doing other stuffs between client requests: {}".format(e))
#         pass
#
#     wifiConnection.checkConnection()
#
#
# try:
#     print("Starting app...")
#     gc.collect()
#     time.sleep(3)
#     wifiConnection: wifi.Wifi = wifi.Wifi()
#     ledStrip = WS2812B(0, 30)
#     ledStrip.rainbow_step()
#     while True:
#         serve(wifiConnection)
#         print("Check light state")
#         if lightEnabled:
#             print("light enabled")
#             ledStrip.rainbow_step()
#         else:
#             print("light disabled")
#             ledStrip.clear()
#
#         time.sleep(0.05)
#
# except KeyboardInterrupt:
#     print("KeyboardInterrupt")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")
# finally:
#     wifiConnection.socketOpened.close()
