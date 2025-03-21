# Pico-Home-Hub


 ## System Architecture 📊

                ┌────────────────────────┐
                │     Home Server        │
                │ (Domoticz or Spring)   │
                └────────────┬───────────┘
                             │ HTTP Requests/Responses
                             ▼
         ┌──────────────────────────────┐
         │      Pico-Home-Hub Devices   │
         │ (Raspberry Pi Pico + Sensors │
         │   or Actuators, MicroPython) │
         └────────────┬─────────────────┘
                      │ Local Network Only
                      ▼
              ┌───────────────────┐
              │   User Devices    │
              │ (Phone, Browser)  │
              └───────────────────┘
- Pico devices communicate with the server via HTTP requests (GET/POST) over your local Wi-Fi network.
- The server (Domoticz or future Spring Boot app) handles requests, device management, and optional data storage.
- No data leaves your local network — ensuring full privacy and offline functiona

## 📄 Project Data Sheet

| Property                   | Details                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| **Project Name**          | Pico-Home-Hub                                                           |
| **Platform**              | Raspberry Pi Pico (MicroPython)                                         |
| **Communication**         | HTTP (Local Network Only)                                               |
| **Privacy**               | 100% Local Data – No external/cloud communication                       |
| **Compatible Server**     | Domoticz on Raspberry Pi 4B or custom Spring Boot + MongoDB (planned)   |
| **Target Users**          | DIY Enthusiasts, Makers, Smart Home Developers                          |
| **License**               | MIT (or your choice)                                                    |
| **Status**                | Active Development                                                      |

## 🚀 Roadmap

| Feature/Component                                 | Status            |
|--------------------------------------------------|-------------------|
| HTTP communication between Pico and server       | ✅ Implemented     |
| Support for basic sensors (e.g., DHT22, PIR)     | ✅ Implemented     |
| Domoticz integration on Raspberry Pi 4B          | ✅ Supported       |
| Server application using Spring Boot + MongoDB   | 🔄 In development  |
| Web UI for device control and monitoring         | 🔄 Planned         |
| MQTT protocol support (optional) with Apache Kafka| 🔄 Planned         |
| OTA updates for Pico devices                     | 🔄 Planned         |
| Secure communication (e.g., HTTPS/Token auth)    | 🔄 Planned         |


## Example config.py
```
WIFI_SSID = 'Your-network-name'
WIFI_PASSWORD = 'secretpass'
IP_ADDRESS = '192.168.0.12'
SUBNET_MASK = '255.255.255.0'
GATEWAY = '192.168.0.1'
DNS = '8.8.8.8'
```

## Execution
1. Add config.py described above.
2. Change pico3.py to main.py.
3. Copy whole files structure to Raspeberry Pi Pico (W).
[.uf2 file must be added to pico for micropython support](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython)

# How does it work 

## WiFi library
In the main file, the program will attempt to connect to the WiFi network using the data provided in `config.py`. This operation is handled in a loop. Once a network connection is established, the library will attempt to open a socket on port 80.

If the operation is unsuccessful, the machine will be restarted to release resources and prevent errors related to improper socket closure.

After successfully opening the socket, the program will wait for client connections (API requests).

The opened socket will throw timeout error after 5 seconds if no client connections are received. This behavior is intentional, allowing the program to perform other tasks, such as checking the WiFi connection.

If the WiFi connection is lost, the library will continuously attempt to reconnect in an infinite loop. 
Once the WiFi connection is successfully restored, the program will check if the socket is still open. If the socket is not open, the program will attempt to reopen it, which may trigger the machine restart described above.

## Request library
The request library is designed to handle received HTTP requests. When the socket receives a message from a client, it is a byte object. The main program converts this byte object into a string, which may look like this:
```
b'GET /switch-one/off HTTP/1.1\r\nX-REPONSE-TYPE: 1[...]\r\n\r\n'
```

The role of the request library is to decode provided string in the following way:
1. Based on the start of the string, the library sets `requestMethod` field to one of the following:
- GET
- POST
- PUT
- DELETE

The request method is an enum type implemented as a singleton with `str` values.

2. From the next part of the string, the library extracts the requested endpoint and assigns it to the `endpoint` variable.
3. The library also checks if `X-REPONSE-TYPE` header is provided. This header is used to manage `Content-Type` header and can take the following values:

- 1 - For the JSON type.
- 2 - For the TEXT/HTML type <b>(default)</b>.

The response type is stored in a variable named `responseType`. This variable is represented by an enum, also implemented as a singleton with str values.
