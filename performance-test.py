#!/usr/bin/env python

import time

from ina219 import INA219, drivers


SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.2

READS = 100


ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS,
             i2c_driver=drivers.auto(interface=1))


def init():
    ina.configure(ina.RANGE_16V, ina.GAIN_AUTO)


def read():
    for x in range(0, READS):
        ina.voltage()


if __name__ == "__main__":
    init()
    start = time.time()
    read()
    finish = time.time()
    elapsed = (finish - start) * 1000000
    print("Read time (average over %d reads): %d microseconds" %
          (READS, int(elapsed / READS)))
