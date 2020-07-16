"""My own damned as3935 driver"""
import time
import spidev

# private constants

_DIRECT_COMMAND = 0x96
_DISTURB_OFF_CMD = 0x20
_ZERO = 0x00
_INDOOR = 0x12
_OUTDOOR = 0x0e

# data registers

_AFE_GAIN = 0x00
_THRESHOLD = 0x01
_LIGHTNING_REG = 0x02
_INT_MASK_ANT = 0x03
_ENERGY_LIGHT_LSB = 0x04
_ENERGY_LIGHT_MSB = 0x05
_ENERGY_LIGHT_MMSB = 0x06
_DISTANCE = 0x07
_FREQ_DISP_IRQ = 0x08

# calibration registers
_CALIB_TRCO = 0x3A
_CALIB_SRCO = 0x3B
_DEFAULT_RESET = 0x3C
_CALIB_RCO = 0x3D

# bit mask ants

_POWER_MASK = 0x01
_GAIN_MASK = 0x3E
_SPIKE_MASK = 0x0F
_IO_MASK = 0xC1
_DISTANCE_MASK = 0xC0
_INT_MASK = 0xF0
_THRESH_MASK = 0x0F
_R_SPIKE_MASK = 0xF0
_ENERGY_MASK = 0xF0
_CAP_MASK = 0x0F
_LIGHT_MASK = 0xCF
_DISTURB_MASK = 0xDF
_NOISE_FLOOR_MASK = 0x70
_OSC_MASK = 0xE0
_SPI_READ_MASK = 0x40
_CALIB_MASK = 0x7F
_DIV_MASK = 0x3F

class AS3935(object):

    def __init__(self, bus=0, channel=0):
        self.spi = self._setup_spi(bus, channel)

    @property
    def power_down(self):
        """Power down the AS3935
           Register 0x00 Bits [0:0]"""
        reply = self.read_register(_AFE_GAIN)
        return reply[-1] & _POWER_MASK

    @power_down.setter
    def power_down(self, value):
        self._write_register_bits(_AFE_GAIN, _POWER_MASK, value, 0)

    @property
    def distance(self):
        reply = self._read_register(_DISTANCE)
        return reply[-1] & _DIV_MASK

    @property
    def energy(self):
        value = self._read_register(_ENERGY_LIGHT_MMSB)[-1]
        # Only first four bits of MMSB are valid
        value &= ~_ENERGY_MASK
        energy = value << 16
        # Get the MSB
        value = self._read_register(_ENERGY_LIGHT_MSB)[-1]
        energy |= value << 8
        # Get the LSB
        value = self._read_register(_ENERGY_LIGHT_LSB)[-1]
        energy |= value
        return energy

    def interrupt(self):
        reply = self._read_register(_INT_MASK_ANT)
        # print(reply)
        return reply[-1] & 0x0f

    def mask_disturbers(self, on_off):
        value = 0
        if on_off:
            value = 1 << 5
        msg = [_INT_MASK_ANT, value]
        reply = self.spi.xfer2(msg)

    def indoor(self, indoor=True):
        value = _OUTDOOR << 1
        if indoor:
            value = _INDOOR << 1
        print("Value = {}".format(value))
        reply = self._write_register(_AFE_GAIN, value)
        return reply

    def threshold(self, value):
        """Threshold is bits [3:0] - Save the others before storing the value"""
        current = self._read_register(_THRESHOLD)[-1]
        updated = (current & _R_SPIKE_MASK) | (value & _SPIKE_MASK)
        print("\n---- setting threshold ----")
        print("register value before : 0b{:08b}".format(current))
        print("register value after  : 0b{:08b}".format(updated))
        reply = self._write_register(_THRESHOLD, updated)
        return reply

    @property
    def noise_floor(self):
        reply = self.read_register(_THRESHOLD)
        value = (reply[-1] & _NOISE_FLOOR_MASK) >> 4
        return value

    @noise_floor.setter
    def noise_floor(self, value):
        """Noise floor is bits [6:4]"""
        if value < 1 or value > 7:
            raise ValueError("Noise level must be from 1 to 7")
        self._write_register_bits(_THRESHOLD, _NOISE_FLOOR_MASK, value, 4)

    def calibrate(self):
        self._write_register(_CALIB_RCO, _DIRECT_COMMAND)
        time.sleep(0.002)
        self._write_register_bits(_FREQ_DISP_IRQ, _OSC_MASK, 1, 5)
        time.sleep(0.002)
        self._write_register_bits(_FREQ_DISP_IRQ, _OSC_MASK, 0, 5)
        time.sleep(0.002)

    def set_defaults(self):
        reply = self._write_register(_DEFAULT_RESET, _DIRECT_COMMAND)
        return reply[-1]

    def _read_register(self, register):
        msg = [register | _SPI_READ_MASK, _ZERO]
        reply = self.spi.xfer2(msg)
        return reply

    def _write_register(self, register, value):
        msg = [register, value]
        reply = self.spi.xfer2(msg)
        return reply

    def _write_register_bits(self, register, mask, bits, start_position):
        current = self._read_register(register)[-1]
        current &= (~mask)
        current |= (bits << start_position)
        self._write_register(register, current)

    def _setup_spi(self, bus, channel, mode=1):
        spi = spidev.SpiDev(bus, channel)
        spi.max_speed_hz = 1200000
        spi.mode = mode
        return spi
