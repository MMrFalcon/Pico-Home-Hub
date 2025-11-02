import dht
import machine
from time import sleep

class DHT_Data:
    def __init__(self, sensor: "DHT_Sensor"):
        self.sensor = sensor
        self.temperature = None
        self.humidity = None

    def read(self):
        self.sensor._dhtObject.measure()
        self.temperature = str(self.sensor._dhtObject.temperature())
        self.humidity = str(self.sensor._dhtObject.humidity())
        return self


class DHT_Sensor:
    def __init__(self, gpio_pin: int):
        self._pin = gpio_pin
        self._init_sensor()

    def _init_sensor(self):
        self._dhtObject = dht.DHT22(machine.Pin(self._pin))

    def get_data(self) -> DHT_Data:
        data = DHT_Data(self)
        return data.read()

while(1):
    # printData()
    # sleep(2)
    sensor = DHT_Sensor(0)
    data: DHT_Data = sensor.get_data()
    print(data.temperature + " (C)")
    print(data.humidity + " %")
    sleep(2)