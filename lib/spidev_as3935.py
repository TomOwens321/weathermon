"""My own damned as3935 driver"""
import spidev

# private constants

_DIRECT_COMMAND = 0x96
_DISTURB_OFF_CMD = 0x20
_ZERO = 0x00

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

    def set_defaults(self):
        msg = [_DEFAULT_RESET, _DIRECT_COMMAND]
        reply = self.spi.xfer2(msg)
        return reply[-1]

    def _read_register(self, register):
        msg = [register | _SPI_READ_MASK, _ZERO]
        # print("Out Message {}".format(msg))
        reply = self.spi.xfer2(msg)
        # print("In  Message {}".format(reply))
        return reply

    def _setup_spi(self, bus, channel, mode=1):
        spi = spidev.SpiDev(bus, channel)
        spi.max_speed_hz = 1200000
        spi.mode = mode
        return spi
