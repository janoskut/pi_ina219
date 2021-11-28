#!/usr/bin/env python

import importlib
import logging
import struct
from typing import cast, List, Optional

from ina219 import INA219, I2cDevice


class SmbusI2cDevice(I2cDevice):

    def __init__(self, interface: int, address: int) -> None:
        from smbus import SMBus  # type: ignore
        super().__init__()
        self._i2c = SMBus(interface)
        self._addr = address

    def write(self, register: int, data: bytes) -> None:
        self._i2c.write_i2c_block_data(self._addr, register,
                                       [int(b) for b in data])

    def read_word(self, register: int, signed: bool = False) -> int:
        data = cast(List[int],
                    self._i2c.read_i2c_block_data(self._addr, register, 2))
        return cast(int,
                    struct.unpack('>h' if signed else '>H', bytes(data))[0])

    @classmethod
    def create(cls, interface: int, address: int) -> 'SmbusI2cDevice':
        return cls(interface, address)


class Smbus2I2cDevice(SmbusI2cDevice):

    def __init__(self, interface: int, address: int) -> None:
        from smbus2 import SMBus  # type: ignore
        self._i2c = SMBus(interface)
        self._addr = address


class AdafruitI2cDevice(I2cDevice):

    def __init__(self, interface: int, address: int) -> None:
        import Adafruit_GPIO.I2C as I2C  # type: ignore
        super().__init__()
        self._i2c = I2C.get_i2c_device(address=address, busnum=interface)

    def write(self, register: int, data: bytes) -> None:
        self._i2c.writeList(register, data)

    def read_word(self, register: int, signed: bool = False) -> int:
        if signed:
            return cast(int, self._i2c.readS16BE(register))
        return cast(int, self._i2c.readU16BE(register))

    @classmethod
    def create(cls, interface: int, address: int) -> 'AdafruitI2cDevice':
        return cls(interface, address)


def find_i2c_driver(interface: int, address: int,
                    prefer: Optional[str] = None) -> I2cDevice:

    def _attempt_import(module: str) -> bool:
        success = False
        try:
            importlib.import_module(module)
            success = True
        finally:
            return success

    drivers = {
        'smbus2': Smbus2I2cDevice,
        'smbus': SmbusI2cDevice,
        'Adafruit_GPIO.I2C': AdafruitI2cDevice,
    }

    if prefer and prefer in drivers:
        drivers = {prefer: drivers, **drivers}

    for module in drivers:
        if _attempt_import(module):
            logging.info(f'Using I2C driver: {module}')
            return drivers[module].create(interface, address)

    raise ModuleNotFoundError('No compatible I2C module found. '
                              'Supported I2C driver modules are: '
                              f'{list(drivers.keys())}')


LOG_LEVEL = logging.WARN
LOG_FORMAT = '%(asctime)s - %(levelname)s - INA219 %(message)s'


def read():

    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

    SHUNT_OHMS = 0.1
    MAX_EXPECTED_AMPS = 0.2

    i2c_addr = INA219.i2c_addr()

    i2c_device = find_i2c_driver(interface=1, address=i2c_addr)

    ina = INA219(i2c_device, SHUNT_OHMS, MAX_EXPECTED_AMPS)
    ina.configure(ina.RANGE_16V, ina.GAIN_AUTO)

    print("Bus Voltage    : %.3f V" % ina.voltage())
    print("Bus Current    : %.3f mA" % ina.current())
    print("Supply Voltage : %.3f V" % ina.supply_voltage())
    print("Shunt voltage  : %.3f mV" % ina.shunt_voltage())
    print("Power          : %.3f mW" % ina.power())


if __name__ == "__main__":
    read()
