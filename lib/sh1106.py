from machine import Pin, I2C
from framebuf import FrameBuffer, MONO_VLSB

#0x80	Next byte = command, stop after it
#0x00	Multiple commands follow (rarely used)
#0x40	Following bytes = display data
#0xC0	Multiple data bytes follow (not used on SH1106)


# Display off / on
CMD_DISPLAY_OFF        = 0xAE
CMD_DISPLAY_ON         = 0xAF

# Clock divide / oscillator
CMD_SET_DISP_CLOCK_DIV = 0xD5
PARM_DISP_CLOCK_DIV    = 0x80  # typical value

# Multiplex ratio
CMD_SET_MULTIPLEX      = 0xA8
PARM_MULTIPLEX_64      = 0x3F  # 1/64 duty

# Display offset
CMD_SET_DISPLAY_OFFSET = 0xD3
PARM_DISPLAY_OFFSET_0  = 0x00

# Start line
CMD_SET_START_LINE     = 0x40  # plus (start line addr = 0)

# Charge pump (DC-DC control)
CMD_SET_CHARGE_PUMP    = 0xAD
PARM_CHARGE_PUMP_ON    = 0x8B  # note: some modules use 0x8A

# Segment remap
CMD_SEG_REMAP          = 0xA1

# COM output scan direction
CMD_COM_SCAN_DIR       = 0xC8

# COM pins hardware configuration
CMD_SET_COM_PINS       = 0xDA
PARM_COM_PINS_64       = 0x12

# Contrast (Brightness)
CMD_SET_CONTRAST       = 0x81
PARM_CONTRAST_DEFAULT  = 0x80

# Pre-charge period
CMD_SET_PRECHARGE      = 0xD9
PARM_PRECHARGE_DEFAULT = 0x22

# VCOMH Deselect Level
CMD_SET_VCOMH_DESEL    = 0xDB
PARM_VCOMH_DEFAULT     = 0x30

# Resume to RAM content display
CMD_ENTIRE_DISPLAY_RAM = 0xA4

# Normal display (not inverted)
CMD_SET_NORMAL_DISPLAY = 0xA6

# --- FONT ---
# Just for testing purposes. FrameBuffer will be used instead.
# Each character is 5 columns wide and 8 rows high.
# Each byte represents a column of 8 pixels (LSB at the top).
# For example, letter "H":
# H:    0x7F = 01111111 vertical: ------      
# font = {
#     "H": [0x7F,0x08,0x08,0x08,0x7F],
#     "e": [0x38,0x44,0x44,0x3C,0x40],
#     "l": [0x00,0x41,0x7F,0x40,0x00],
#     "o": [0x38,0x44,0x44,0x38,0x00],
#     "W": [0x7C,0x02,0x01,0x02,0x7C],
#     "r": [0x7C,0x08,0x04,0x04,0x00],
#     "d": [0x38,0x44,0x44,0x7F,0x00],
#     " ": [0x00,0x00,0x00,0x00,0x00]
# }


class SH1106:

    # Print text on the display.
    # param text: text to print
    # param column: column number to print the text available columns: 
    #   1-6 for 128x64 display with 8 pixel high font and 2 pixel spacing
    # param clearScreen: if True clear the screen before printing
    def printText(self, text: str, column: int = 1, clearScreen: bool = True):
        print(text)
        if clearScreen:
            self.clear_screen()
        # TODO check how many lines fit on the display
        # TODO 10 should be constant for line height
        self.frameBuffer.text(text, 0, column * 10)
        self.show()
        

    def __init__(self, i2c, addr, width=128, height=64):
        self.i2c = i2c
        self.addr = addr
        self.width = width
        self.height = height
        self.offset = 2
        self.pages = height // 8
        self.buffer = bytearray(width * self.pages)
        self.init_display()
        self.frameBuffer = FrameBuffer(self.buffer, self.width, self.height, MONO_VLSB)
        self.max_lines = height // 10  # assuming 10 pixels per text line

    # For 8x8 matrix clear all lines
    def clear_screen(self):
        self.clear_text_line(self.frameBuffer, 0)
        self.clear_text_line(self.frameBuffer, 1)
        self.clear_text_line(self.frameBuffer, 2)
        self.clear_text_line(self.frameBuffer, 3)
        self.clear_text_line(self.frameBuffer, 4)
        self.clear_text_line(self.frameBuffer, 5)
        self.clear_text_line(self.frameBuffer, 6)
        self.clear_text_line(self.frameBuffer, 7)

    # Write to an address register command
    # 1 0 000000 = 1000 0000 = 0x80 the next byte is a command.
    # Co = 1  (last control byte)
    # D/C = 0 (command)
    # c the command byte
    # Final result b'\x80\xae' -> next byte is command 0xae (display off).
    def cmd(self, c):
        print("CMD:")
        print(b'\x80' + bytes([c]))
        self.i2c.writeto(self.addr, b'\x80' + bytes([c]))

    # Write to a data register data
    # 0 1 000000 = 0100 0000 = 0x40 the next byte is data.
    # Co = 0  (more data bytes to follow)
    # D/C = 1 (data)
    # d the data byte
    # Final result b'\x40\xff' -> next byte is data 0xff.
    def data(self, d):
        self.i2c.writeto(self.addr, b'\x40' + bytes([d]))

    def init_display(self):
        for c in (
            CMD_DISPLAY_OFF,
            CMD_SET_DISP_CLOCK_DIV, PARM_DISP_CLOCK_DIV,
            CMD_SET_MULTIPLEX, PARM_MULTIPLEX_64,
            CMD_SET_DISPLAY_OFFSET, PARM_DISPLAY_OFFSET_0,
            CMD_SET_START_LINE,
            CMD_SET_CHARGE_PUMP, PARM_CHARGE_PUMP_ON,
            CMD_SEG_REMAP,
            CMD_COM_SCAN_DIR,
            CMD_SET_COM_PINS, PARM_COM_PINS_64,
            CMD_SET_CONTRAST, PARM_CONTRAST_DEFAULT,
            CMD_SET_PRECHARGE, PARM_PRECHARGE_DEFAULT,
            CMD_SET_VCOMH_DESEL, PARM_VCOMH_DEFAULT,
            CMD_ENTIRE_DISPLAY_RAM,
            CMD_SET_NORMAL_DISPLAY,
            CMD_DISPLAY_ON
        ):
            self.cmd(c)

    def show(self):
        for page in range(self.pages):
            self.cmd(0xB0 | page)
            col = self.offset
            self.cmd(0x00 | (col & 0x0F))
            self.cmd(0x10 | (col >> 4))
            start = page * self.width
            end = start + self.width
            for b in self.buffer[start:end]:
                self.data(b)

    # Method fill clear the pixels in the framebuffer on the given line.
    # For 8x8 matrix the height is 9 pixels because 1-2 pixel is space between lines.
    def clear_text_line(self, fb:FrameBuffer, line, height=10):
        y = line * height
        fb.fill_rect(0, y, self.width, height, 0)

#     # --- PIXEL RENDER for custom font drawing test ---
#     def pixel(self, x: int, y: int, showPixel: bool):
#         page = y >> 3
#         bit = 1 << (y & 7)
#         idx = page * self.width + x
#         if showPixel:
#             self.buffer[idx] |= bit
#         else:
#             self.buffer[idx] &= ~bit


# # --- CUSTOM FONT DRAWING TEST FUNCTIONS ---
# def draw_char(display: SH1106, x, y, ch):
#     if ch not in font:
#         ch = " "
#     columns = font[ch]
#     for col_idx, col in enumerate(columns):
#         for row in range(7):
#             if (col >> row) & 1:
#                 display.pixel(x + col_idx, y + row, 1)

# def draw_text(display: SH1106, x: int, y: int, text: str):
#     for ch in text:
#         draw_char(display, x, y, ch)
#         x += 6

## test
## 128 x 64 display
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
devices = i2c.scan()
for device in devices:
    print(device)
    print(hex(device))

# 0x3c known from print(hex(device))
# needed for client app.
oled: SH1106 = SH1106(i2c, 0x3c)
oled.printText("Hello", 1, clearScreen=False)
oled.printText("World", 2, clearScreen=False)

# Draw text using custom font rendering
# draw_text(oled, 0, 0, "Hello")
# draw_text(oled, 0, 10, "World")

# fb = FrameBuffer(oled.buffer, oled.width, oled.height, MONO_VLSB)

# # Draw text instantly using built-in font
# fb.text("Hello", 0, 0)
# fb.text("World", 0, 10)

# oled.show()
# oled.clear_text_line(fb, 0)
# oled.clear_text_line(fb, 1)
# oled.clear_text_line(fb, 2)
# oled.clear_text_line(fb, 3)
# oled.clear_text_line(fb, 4)
# oled.clear_text_line(fb, 5)
# oled.clear_text_line(fb, 6)
# oled.clear_text_line(fb, 7)
# # oled.clear_line_buffer(0)
# # oled.clear_line_buffer(10)
# oled.show()

# fb.text("Test", 0, 0)
# fb.text("ds", 0, 10)

# oled.show()
# print("V3")
