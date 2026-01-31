import machine, neopixel, time

class WS2812B:
    BRIGHTNESS = 0.3

    def __init__(self, pin: int, ledsCount: int):
        self.ledsCount = ledsCount
        self.pin = machine.Pin(pin)
        self.np = neopixel.NeoPixel(self.pin, ledsCount)
        self.j = 0  # stan animacji

    def scaled(self, r, g, b):
        return (int(r * self.BRIGHTNESS),
                int(g * self.BRIGHTNESS),
                int(b * self.BRIGHTNESS))

    def wheel(self, pos):
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)

    def rainbow_step(self):
        for i in range(self.ledsCount):
            rc_index = (i * 256 // self.ledsCount + self.j) & 255
            self.np[i] = self.scaled(*self.wheel(rc_index))
        self.np.write()
        self.j = (self.j + 1) % 256

    def clear(self):
        for i in range(self.ledsCount):
            self.np[i] = (0, 0, 0)
        self.np.write()
