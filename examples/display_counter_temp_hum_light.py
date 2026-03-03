# Example to display temperature, humidity and light level on SH1106 OLED display
import lib.DHT22 as DHT22
import lib.sh1106 as sh1106
import lib.oky16560 as oky16560
from time import sleep
from machine import Pin, I2C



sensor = DHT22.DHT_Sensor(0)
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
oled: sh1106.SH1106 = sh1106.SH1106(i2c, 0x3c)
lightSensor = oky16560.Oky16560()


def printData():
    data: DHT22.DHT_Data = sensor.get_data()
    temperature = data.temperature + " (C)"
    humidity = data.humidity + " %"
    lightValue = lightSensor.get_light_level()
    print(lightValue)
    print(temperature)
    print(humidity)
    oled.printText("Temp: " + temperature, 1, clearScreen=True)
    oled.printText("Hum: " + humidity, 2, clearScreen=False)
    oled.printText(lightValue, 3, clearScreen=False)
    sleepTime = 30
    for i in range(sleepTime):
        oled.clear_text_line(oled.frameBuffer, 4)
        oled.printText("Next in: {}s".format(sleepTime - i), 4, clearScreen=False)
        sleep(1)
    # sleep(30)

while(1):
    printData()