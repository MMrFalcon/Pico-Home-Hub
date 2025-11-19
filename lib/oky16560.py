# Light sensor module for Oky-16560 device
from machine import ADC, Pin
import time

 # AO -> GP26/ADC0 adc = ADC(Pin(26)) 
# 35000 is dark, 10000 is bright
# 0 - 10000: bright light
# 10000 - 15000: normal room light
# LIGHT NOT OK:
# 15000 - 20000: dim room light
# 32776 - 35000: 4k lumen office light dim
# NIGHT OR SHADE
# 42000: shade on lumen office light
# NIGHT
# 50000 > - dark light 
twilight = 35000  # ??
DARK_THRESHOLD = 35000  
MIDDLE_THRESHOLD = 15000 
LIGHT_THRESHOLD = 20000 

class Oky16560:
    adc = None

    def __init__(self, pin: int = 26):
        self.adc = ADC(pin)  # AO -> GP26/ADC0

    def _read_light(self) -> int:
        samples = 20
        total = 0
        for _ in range(samples):
            total += self.adc.read_u16()
            time.sleep(0.005)
        return total // samples
    
    def get_light_level(self) -> str:
        light_value = self._read_light()
        if light_value >= DARK_THRESHOLD:
            return "DARK, {}".format(light_value)
        elif light_value >= LIGHT_THRESHOLD:
            return "SHADE, {}".format(light_value)
        elif light_value >= MIDDLE_THRESHOLD:
            return "NORMAL LIGHT, {}".format(light_value)
        else:
            return "BRIGHT LIGHT, {}".format(light_value)

# Example usage
# while True:
#     light_lvl = Oky16560().get_light_level()  
#     print(light_lvl)