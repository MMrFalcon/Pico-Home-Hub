import machine, onewire, ds18x20, time

class DS18B20:
  dsPin = None
  dsSensor = None
  roms = None

  def __init__(self, dataPin: int):
    self.dsPin = machine.Pin(dataPin)
    self.dsSensor = ds18x20.DS18X20(onewire.OneWire(self.dsPin))
    self.roms = self.dsSensor.scan()
    print('Found DS devices: ', self.roms)

  def redTemp(self) -> str:
    if (self.dsPin == None or self.dsSensor == None ):
      raise Exception("Device not configured properly, try again")
    self.dsSensor.convert_temp()
    time.sleep_ms(750)
    for rom in self.roms:
      print(rom)
      tempC = self.dsSensor.read_temp(rom)
      tempFormatted = "{:.2f}".format(tempC)
      print('temperature (C):', tempFormatted)
      return tempFormatted
