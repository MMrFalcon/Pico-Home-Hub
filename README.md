# Pico-Home-Hub


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