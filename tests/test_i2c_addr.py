import sys
import logging
import unittest

from ina219 import INA219


logger = logging.getLogger()
logger.level = logging.ERROR
logger.addHandler(logging.StreamHandler(sys.stdout))


class TestI2cAddr(unittest.TestCase):

    def test_i2c_addr_combinations(self):

        # format: <addr>: (<a1>, <a0>)
        configurations = {
            0b1000000: ('GND', 'GND'),
            0b1000001: ('GND', 'VSP'),
            0b1000010: ('GND', 'SDA'),
            0b1000011: ('GND', 'SCL'),
            0b1000100: ('VSP', 'GND'),
            0b1000101: ('VSP', 'VSP'),
            0b1000110: ('VSP', 'SDA'),
            0b1000111: ('VSP', 'SCL'),
            0b1001000: ('SDA', 'GND'),
            0b1001001: ('SDA', 'VSP'),
            0b1001010: ('SDA', 'SDA'),
            0b1001011: ('SDA', 'SCL'),
            0b1001100: ('SCL', 'GND'),
            0b1001101: ('SCL', 'VSP'),
            0b1001110: ('SCL', 'SDA'),
            0b1001111: ('SCL', 'SCL'),
        }

        for addr, conf in configurations.items():
            conf_a0 = INA219.I2cAddrAx[conf[1]]
            conf_a1 = INA219.I2cAddrAx[conf[0]]
            with self.subTest(msg="Testing if (a0,a1)=>addr",
                              a0=conf[0], a1=conf[1], addr=addr):
                self.assertEqual(INA219.i2c_addr(a0=conf_a0, a1=conf_a1), addr)
