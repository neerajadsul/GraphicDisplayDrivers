import board
import busio
import digitalio
import time
import random


print(dir(board))
print(board.board_id)

chip_select = digitalio.DigitalInOut(board.GP17)
chip_select.direction = digitalio.Direction.OUTPUT
chip_select.value = False

data_mode = digitalio.DigitalInOut(board.GP20)
data_mode.direction = digitalio.Direction.OUTPUT

reset_display = digitalio.DigitalInOut(board.GP21)
reset_display.direction = digitalio.Direction.OUTPUT
reset_display.value = True

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

spi = busio.SPI(board.GP18, board.GP19)


class EaDogs102:
    MODE_CMD = False
    MODE_DATA = True

    def __init__(self, spi, chip_select, mode, reset):
        self.spi = spi
        while not self.spi.try_lock():
            pass
        # self.spi.configure(polarity=0)
        self.spi.unlock()
        self.chip_select = chip_select
        self.reset = reset
        self.data_mode = mode
        self.data_mode = self.MODE_CMD

    def display_init(self):
        self.data_mode = self.MODE_CMD
        init_sequence = bytes([
            0x40, # display start line 0
            0xA1, # seg reverse
            0xC0, # Normal COM0 to COM63
            0xA4, # Set all pixel on
            0xA6, # Inverse off
            0xA2, # Set bias 1/9
            0x2F, # Booster, Regulator and Follower on
            # Set contrast
            0x27, # Set VLCD Resistor Ratio,
            0x81, # Set electrostatic volume
            0x10,
            0xAF, # Display ON
            0xFA, # Advanced program control 0,
            0xA0,
        ])
        while not self.spi.try_lock():
            pass
        self.spi.write(init_sequence)
        spi.unlock()
        self.data_mode = self.MODE_DATA

    def _write_commands(self, commands):
        self.data_mode = self.MODE_CMD
        time.sleep(0.005)
        while not self.spi.try_lock():
            pass
        self.spi.write(commands)
        self.spi.unlock()

    def _write_data(self, data):
        self.data_mode = self.MODE_DATA
        time.sleep(0.005)
        while not self.spi.try_lock():
            pass
        self.spi.write(data)
        self.spi.unlock()

    def show_data(self):

        page_address = random.randrange(0, 8)
        col_address_lsb = random.randrange(0, 16)
        col_address_msb = random.randrange(0, 16)

        commands = bytes([page_address, col_address_lsb, col_address_msb])

        self._write_commands(commands)
        some_data = bytes([
            random.randrange(0, 127)
        ])
        self._write_data(some_data)



display = EaDogs102(spi=spi, chip_select=chip_select, mode=data_mode, reset=reset_display)
time.sleep(0.005)
print("Init Display")
display.display_init()
print("Display init complete.")
display.show_data()
print("Somedata")
# display._write_commands(bytes([0xAA, 0xE2]))
while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
    display.show_data()

