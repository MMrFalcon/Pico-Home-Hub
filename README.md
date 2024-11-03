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