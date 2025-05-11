'''
Read the internal chip temperature at ADC 4.
'''

import machine
import json

# ADC 4 is connected to internal temperature sensor
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / 65535

def getRawInternalTemp():
    reading = sensor_temp.read_u16() * conversion_factor
    # Formula from Raspberry Pi Pico datasheet
    temperature_c = 27 - (reading - 0.706) / 0.001721
    return temperature_c

def getJsonInternalTemp():
    try:
        temp = getRawInternalTemp()
        return json.dumps({"chipTempC": temp})
    except Exception:
        return json.dumps({})
