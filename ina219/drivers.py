import logging
import struct
from typing import Any, cast, List

from .ina219 import I2cDriver


class SmbusDriver(I2cDriver):

    def __init__(self, smbus: Any) -> None:
        self._i2c = smbus

    def write(self, address: int, register: int, data: bytes) -> None:
        self._i2c.write_i2c_block_data(address, register,
                                       [int(b) for b in data])

    def read_word(self, address: int, register: int,
                  signed: bool = False) -> int:
        data = cast(List[int],
                    self._i2c.read_i2c_block_data(address, register, 2))
        return cast(int,
                    struct.unpack('>h' if signed else '>H', bytes(data))[0])

    @classmethod
    def load(cls, interface: int) -> I2cDriver:
        from smbus import SMBus  # type: ignore
        return cls(SMBus(interface))


class Smbus2Driver(SmbusDriver):

    @classmethod
    def load(cls, interface: int) -> I2cDriver:
        from smbus2 import SMBus  # type: ignore
        return cls(SMBus(interface))


class AdafruitDriver(SmbusDriver):

    @classmethod
    def load(cls, interface: int) -> I2cDriver:
        import Adafruit_PureIO.smbus  # type: ignore
        return cls(Adafruit_PureIO.smbus.SMBus(interface))


def auto(interface: int) -> I2cDriver:

    drivers = [Smbus2Driver, SmbusDriver, AdafruitDriver]

    for driver in drivers:
        try:
            loaded = driver.load(interface)
            logging.info(f'Auto-loading I2C driver: {driver.__name__}')
            return loaded
        except ImportError:
            pass

    raise ModuleNotFoundError('No compatible I2C module found. '
                              'Supported I2C driver modules are: '
                              f'{[d.__name__ for d in drivers]}')
