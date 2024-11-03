from machine import Pin
import time

"""
From the datasheet:
A command byte initiates each data transfer. 
    - The MSB (bit 7) must be a logic 1. If it is 0, writes to the DS1302 will be disabled. 
    - Bit 6 specifies clock/calendar data if logic 0 or RAM data if logic 1.
    - Bits 1 to 5 specify the designated registers to be input or output.
    - LSB (bit 0) specifies a write operation (input) if logic 0 or read operation (output) if logic 1. 
The command byte is always input starting with the LSB (bit 0). 
Example write/read command: 10000000 (0x80) binary (LSB 0 - write / LSB 1 - read).
Before start write operation we must disable write protection by send 0 to RTC_REG_WRITE_PROTECTION registry.

## READ DATA FROM SECONDS REGISTRY ##
CH (Bit 7): "1" indicates that the clock is halted.
10 SEC (Bits 6-4): "000" - This represents the tens digit of the seconds.
SEC (Bits 3-0): "0100" - This represents the units digit of the seconds.
Read and write data use BCD format.
"""

"""10000000 write value, accepted data: 0 - 59. 10000001 (0x81) read in BCD format"""
RTC_SEC_WRITE = (0x80)
RTC_SEC_READ = (0x81)
"""10000010 binary, accepted data: 0 - 59"""
RTC_MIN_WRITE = (0x82)
RTC_MIN_READ = (0x83)
"""10000100 binary, accepted data: 01-12/00-23"""
RTC_HOUR_WRITE = (0x84)
RTC_HOUR_READ = (0x85)
"""10000110 binary 01-28/29, accepted data: 01-30, 01-31"""
RTC_DAY_OF_THE_MONTH_WRITE = (0x86)
RTC_DAY_OF_THE_MONTH_READ = (0x87)
"""10001000 binary, accepted data: 01 - 12"""
RTC_MONTH_WRITE = (0x88)
RTC_MONTH_READ = (0x89)
"""10001010 binary, accepted data: 01-07"""
RTC_DAY_OF_THE_WEEK_WRITE = (0x8A)
RTC_DAY_OF_THE_WEEK_READ = (0x8B)
"""10001100 binary, accepted data: 00-99"""
RTC_YEAR_WRITE = (0x8C)
RTC_YEAR_READ = (0x8D)

"""
Bit 7 of the control register is the write-protect bit. The first seven bits (bits 0 – 6) are forced to 0 and
will always read a 0 when read. Before any write operation to the clock or RAM, bit 7 must be 0
10001110 binary, accepts 00000000 for write, and 10000000 for read (0x80)
""" 
RTC_REG_WRITE_PROTECTION = (0x8E)
"""10010000 binary"""
RTC_REG_TRICKLE_CHARGER = (0x90)
"""11000000 binary"""
RTC_REG_RAM_0 = (0xC0)

"""
At the beginning of a clock burst read, the current time is transferred to a second set of registers. The
time information is read from these secondary registers, while the clock may continue to run. This
eliminates the need to re-read the registers in case of an update of the main registers during a read.
10111110 binary.
"""
RTC_CLOCK_BURST_MODE = (0xBE)

"""DEFAULT GPIO PIN NUMBERS"""
CLK_PIN = Pin(6)
DAT_PIN = Pin(7)
CS_RST_PIN = Pin(4)

class DS1302:
    _year_prefix = '20'
    def __init__(self, clk, dio, cs_rst):
        self.clk = clk
        self.dio = dio
        self.cs_rst = cs_rst
        self.clk.init(Pin.OUT)
        self.cs_rst.init(Pin.OUT)

    """ 
    Bit-banging SPI communication.
    Write bit from LSB to MSB.
    For 10000000 (0x80), will sent 0,0,0,0,0,0,0,1. LSB 0 in COMMAND BYTE specifies a write operation
    10000000 >> 0 = 10000000; 10000000 & 1 (get LSB) = 0; (10000000 & 00000001) = 0
    10000000 >> 1 = 1000000; 1000000 & 1 = 0 etc.
    """ 
    def _write_byte(self, byte):
        self.dio.init(Pin.OUT)
        for i in range(8):
            byte_to_write = (byte >> i) & 1
            self.dio.value(byte_to_write)
            self._sample_data_on_the_raising_edge_of_the_clock()

    """    
    Note that the first data bit to be transmitted occurs on the first falling edge after the last bit
    of the command byte is written.
    Data contained in the clock/ calendar registers is in binary coded decimal format (BCD)
    """
    def _read_byte(self):
        self.dio.init(Pin.IN)
        data = 0
        for i in range(8):
            bit_value = self.dio.value()
            data = data | (bit_value << i)
            self._sample_data_on_the_raising_edge_of_the_clock()
        return data

    def _sample_data_on_the_raising_edge_of_the_clock(self):
        self.clk.value(1)
        self.clk.value(0)

    def _write_data_to_register(self, register, data):
        self.cs_rst.value(1)
        self._write_byte(register)
        self._write_byte(data)
        self.cs_rst.value(0)
    
    def _unlock_then_write(self, register, data):
        dataInBcd = self._int_to_bcd(data)
        self._write_data_to_register(RTC_REG_WRITE_PROTECTION, 0)
        self._write_data_to_register(register, dataInBcd)
        self._write_data_to_register(RTC_REG_WRITE_PROTECTION, 0x80)

    def _read_from_regiter(self, register):
        self.cs_rst.value(1)
        self._write_byte(register)
        data_readed = self._read_byte()
        self.cs_rst.value(0)
        return self._bcd_to_string(data_readed)
    
    def _prepare_year_for_save(self, year):
        yearAsString = str(year)
        return int(yearAsString[2:4])
    
    """
    0x0F = 00001111. 10000100 >> 4 = 0000 1000. 0000 1000 & 00001111 = 0000 1000
    """
    def _bcd_to_string(self, bcd_value):
        tens_digit = (bcd_value >> 4) & 0x0F  
        units_digit = bcd_value & 0x0F

        tens_digit_decimal = tens_digit * 10
        units_digit_decimal = units_digit

        result_string = str(tens_digit_decimal + units_digit_decimal)

        return result_string
    
    """
    When we get number from registry it's formatted to BCD code.
    It always has 8 bit. First 4 bits represents decimal value: 2 = 0010
    Left shifting by 4 will return 0010 0000.
    Units part also has 4 bit, value 3 = 0011. When we perform OR operation we get following result:
    0010 0000 | 0000 0011 = 0010 0011
    """
    def _int_to_bcd(self, integer_value):

        if integer_value < 0 or integer_value > 99:
            raise ValueError("Input must be in the range [0, 99]")

        tens_digit = integer_value // 10
        units_digit = integer_value % 10

        bcd_value = (tens_digit << 4) | units_digit
        return bcd_value

    """
    ###################### Public API ################################
    """ 
    def writeSeconds(self, seconds):
        self._unlock_then_write(RTC_SEC_WRITE, seconds)

    def readSeconds(self):
        return self._read_from_regiter(RTC_SEC_READ)

    def writeMinutes(self, minutes):
        self._unlock_then_write(RTC_MIN_WRITE, minutes)

    def readMinutes(self):
        return self._read_from_regiter(RTC_MIN_READ)
    
    def writeHours(self, hours):
        self._unlock_then_write(RTC_HOUR_WRITE, hours)

    def readHours(self):
        return self._read_from_regiter(RTC_HOUR_READ)
    
    def writeDayOfTheMonth(self, dayOfTheMonth):
        self._unlock_then_write(RTC_DAY_OF_THE_MONTH_WRITE, dayOfTheMonth)

    def readDayOfTheMonth(self):
        return self._read_from_regiter(RTC_DAY_OF_THE_MONTH_READ)
    
    def writeMonth(self, month):
        self._unlock_then_write(RTC_MONTH_WRITE, month)

    def readMonth(self):
        return self._read_from_regiter(RTC_MONTH_READ)
    
    def writeDayOfTheWeek(self, dayOfTheWeek):
        self._unlock_then_write(RTC_DAY_OF_THE_WEEK_WRITE, dayOfTheWeek)

    def readDayOfTheWeek(self):
        return self._read_from_regiter(RTC_DAY_OF_THE_WEEK_READ)
    
    def writeYear(self, year):
        yearForSave = self._prepare_year_for_save(year)
        self._unlock_then_write(RTC_YEAR_WRITE, yearForSave)

    def readYear(self):
        return self._year_prefix + self._read_from_regiter(RTC_YEAR_READ)
    
    def start(self):
        self._write_byte(RTC_CLOCK_BURST_MODE)

    def getDate(self):
        day = self.readDayOfTheMonth()
        month = self.readMonth()
        year = self.readYear()
        hour = self.readHours()
        min = self.readMinutes()
        sec = self.readSeconds()
        dayOfTheWeek = self.readDayOfTheWeek()
        return "Date: " + day +"." + month + "." + year + ", " + hour + ":" + min + ":" + sec + ", Day: " + dayOfTheWeek

    def setDate(self, dayOfTheMonth, month, year, hour, minute, second, dayOfWeek):
        if (dayOfTheMonth & dayOfTheMonth > 0 & dayOfTheMonth < 32):
            self.writeDayOfTheMonth(dayOfTheMonth)
        if (month & month > 0 & month < 13):
            self.writeMonth(month)
        if (year & year > 0):
            self.writeYear(year)
        if (hour & hour > -1 & hour < 23):
            self.writeHours(hour)
        if (minute & minute > -1 & minute < 60):
            self.writeMinutes(minute)
        if (second & second > -1 & second < 60):
            self.writeSeconds(second)
        if (dayOfWeek & dayOfWeek > 0 & dayOfWeek < 8):
            self.writeDayOfTheWeek(dayOfWeek)


"""Example of use: """
ds = DS1302(CLK_PIN,DAT_PIN,CS_RST_PIN)

# ds.writeDayOfTheMonth(17)
# ds.writeMonth(2)
# ds.writeYear(2024)
# ds.writeHours(21)
# ds.writeMinutes(42)
# ds.writeSeconds(0)
# ds.writeDayOfTheWeek(6)
"""OR"""
# ds.setDate(dayOfTheMonth=17, month=2, year=2024, hour=21, minute=40, second=00, dayOfWeek=6)
"""READ DATE"""
while 1:
    print(ds.getDate())
    time.sleep(1)
