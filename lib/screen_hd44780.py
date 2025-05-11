import time
import sys

class Hd44780:
    # COMMANDS
    """
    00000001
    """
    CLEAR = 0x01 

    """
    00000010
    """
    CURSOR_HOME = 0x02 

    """
    000001 I/D S
    I/D: 0 = decrement cursor position, 1 = increment cursor position;
    S: 0 = no display shift, 1 = display shift;
    COMMAND - 00000110 (increment, no display shift) 
    """
    ENTRY_MODE = 0x06 

    """
    D: 0 = display-off, 1 = display on
    C: 0 = cursor off, 1 = cursor on; 
    B: 0 = cursor blink off, 1 = cursor blink on;
    00001DCB
    COMMAND - 00001100 (Display on, no cursor)
    """
    DISPLAY_ON_SHOW_CURSOR = 0x0C

    """
    00001000
    0x08 for the screen command it will turn OFF the screen.
    """
    DISPLAY_OFF = 0x08

    """
    DL: 0 = 4-bit interface, 1 = 8-bit interface; 
    N: 0 = 1/8 or 1/11 duty (1 line), 1 = 1/16 duty (2 lines); 
    F: 0 = 5×8 dots, 1 = 5×10 dots
    0x28
    001DLNF**
    COMMAND - 00101000 (4 bit , 2 lines, 5x8 dots)
    """
    FUNCTION_TWO_LINES_FOUR_BITS_5x8 = 0x28

    """
    Sets the DDRAM address. Sent and recive the data.
    The DDRAM is 80 bytes (40 per row) addressed with a gap between the two rows. 
    The first row is addresses 0 to 39 decimal or 0 to 27 hex. 
    The second row is addresses 64 to 103 decimal or 40 to 67 hex.
    COMMAND - 10000000 - 0000000 (7 bits after 1) = 0
    """
    LCD_LINE_1 = 0x80

    """
    Sets the DDRAM address. Sent and recive the data.
    The DDRAM is 80 bytes (40 per row) addressed with a gap between the two rows. 
    The first row is addresses 0 to 39 decimal or 0 to 27 hex. 
    The second row is addresses 64 to 103 decimal or 40 to 67 hex.
    11000000 - 1000000 (7 bits after 1) = 40
    """
    LCD_LINE_2 = 0xC0

    """
    00001000
    0x08 is just a bit flag that tells the PCF8574 I/O expander chip to set a pin HIGH.
    It's not a command for the screen but for the I2C adapter.
    """
    BACKLIGHT_ON = 0x08

    """
    00000000
    """
    BACKLIGHT_OFF = 0x00

    COMMAND_REGISTER = 0

    DATA_REGISTER = 1

    def __init__(self, i2c, i2cAddr, lines: int, cols: int):
        self.i2c = i2c
        self.i2cAddr = i2cAddr
        # TODO magic numbers
        self.backlight = self.BACKLIGHT_ON
        self.clockSync = 0x04
        self.lines = lines
        self.cols = cols

    def _initLcd(self):
        time.sleep_ms(20)
        self._writeCommand(0x33)
        self._writeCommand(0x32)
        self._writeCommand(self.FUNCTION_TWO_LINES_FOUR_BITS_5x8)
        self._writeCommand(self.DISPLAY_ON_SHOW_CURSOR)
        self._writeCommand(self.CLEAR)
        self._writeCommand(self.ENTRY_MODE)
        time.sleep_ms(2)

    def _writeCommand(self, command):
        self._i2cSend(command, self.COMMAND_REGISTER)

    def _writeData(self, data):
        self._i2cSend(data, self.DATA_REGISTER)

    def _i2cSend(self, data, register):
        # While connecting via I2C, the LCD works in 4 bit mode. 0xF0 1111 0000
        firstFourBits = data & 0xF0
        secondFourBits = (data << 4) & 0xF0
        self._writeByte(firstFourBits | register) # Put the data.
        self._writeByte(firstFourBits | register | self.clockSync) # Prepare for accept.
        self._writeByte(firstFourBits | register) # clockSync low - accept the byte.
        self._writeByte(secondFourBits | register)
        self._writeByte(secondFourBits | register | self.clockSync)
        self._writeByte(secondFourBits | register)

    def _writeByte(self, data):
        # write byte, keep the backlight on or off.
        self.i2c.writeto(self.i2cAddr, bytes([data | self.backlight]))
        time.sleep_us(50)

    def _backlightOff(self):
        print("Request for set backlight state to OFF")
        self.backlight = self.BACKLIGHT_OFF
        try:
            self._writeCommand(self.CURSOR_HOME)  # Send a no-op byte just to apply the new backlight state
        except Exception as e:
            print("Failed to turn off backlight:", e)

    def _backlightOn(self):
        print("Request for set backlight state to ON")
        self.backlight = self.BACKLIGHT_ON
        try:
            self._writeCommand(self.CURSOR_HOME)
        except Exception as e:
            print("Failed to turn on backlight:", e)

    """
    PUBLIC API
    """
    def clear(self):
        self._writeCommand(self.CLEAR)

    def home(self):
        self._writeCommand(self.CURSOR_HOME)

    def write(self, string):
        for char in string:
            self._writeData(ord(char))

    def turnOff(self):
        try:
            self._writeCommand(self.DISPLAY_OFF)
            self._backlightOff()
        except Exception as e:
            print("Failed to turn off LCD:", e)
            sys.print_exception(e)

    def isAvailable(self) -> bool:
        try:
            self._writeCommand(self.CLEAR) 
            return True
        except Exception as e:
            print("LCD not available:", e)
            return False

