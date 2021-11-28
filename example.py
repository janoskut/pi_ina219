#!/usr/bin/env python

import logging

from ina219 import INA219, drivers


SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.2


def read():

    i2c_addr = INA219.i2c_addr()

    # old interface (internal I2C driver detection)
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=i2c_addr,
                 log_level=logging.INFO)

    # new interface passing explicit I2C driver
    driver = drivers.auto(interface=1)
    # driver = drivers.SmbusDriver.load(interface=1)
    # driver = drivers.Smbus2Driver.load(interface=1)
    # driver = drivers.AdafruitDriver.load(interface=1)
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=i2c_addr,
                 log_level=logging.INFO,
                 i2c_driver=driver)

    ina.configure(ina.RANGE_16V, ina.GAIN_AUTO)

    print("Bus Voltage    : %.3f V" % ina.voltage())
    print("Bus Current    : %.3f mA" % ina.current())
    print("Supply Voltage : %.3f V" % ina.supply_voltage())
    print("Shunt voltage  : %.3f mV" % ina.shunt_voltage())
    print("Power          : %.3f mW" % ina.power())


if __name__ == "__main__":
    read()
