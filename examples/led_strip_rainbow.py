# Script for WS2812B
import machine, neopixel, time
import math

# LEDS COUNT
n = 30
pin = machine.Pin(0)
np = neopixel.NeoPixel(pin, n)

BRIGHTNESS = 0.3

def scaled(r, g, b):
    return (int(r * BRIGHTNESS), int(g * BRIGHTNESS), int(b * BRIGHTNESS))

def wheel(pos):
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def rainbow_cycle(wait):
    j = 0
    while True:
        for i in range(n):
            rc_index = (i * 256 // n + j) & 255
            np[i] = scaled(*wheel(rc_index))
        np.write()
        j = (j + 1) % 256
        time.sleep(wait)

rainbow_cycle(0.05)
