import sys
import logging
import unittest

from mock import Mock, call

from ina219 import INA219, I2cDriver, DeviceRangeError

logger = logging.getLogger()
logger.level = logging.ERROR
logger.addHandler(logging.StreamHandler(sys.stdout))


class TestReadAutoGain(unittest.TestCase):

    GAIN_RANGE_MSG = r"Current out of range \(overflow\)"

    def setUp(self):
        I2cDriver.register(Mock)  # make "Mock" a subclass of "I2cDriver"
        self.i2c = Mock()

    def test_auto_gain(self):
        self.ina = INA219(0.1, 0.4, i2c_driver=self.i2c)
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_AUTO)

        self.ina._read_voltage_register = Mock()
        self.ina._read_voltage_register.side_effect = [0xfa1, 0xfa0]
        self.ina._read_configuration = Mock()
        self.ina._read_configuration.side_effect = [0x99f, 0x99f]
        self.ina._current_register = Mock(return_value=100)

        self.assertAlmostEqual(self.ina.current(), 4.878, 3)

        calls = [call(0x40, 0x05, bytes([0x83, 0x33])),
                 call(0x40, 0x00, bytes([0x09, 0x9f])),
                 call(0x40, 0x05, bytes([0x20, 0xcc])),
                 call(0x40, 0x00, bytes([0x11, 0x9f]))]
        self.i2c.write.assert_has_calls(calls)

    def test_auto_gain_out_of_range(self):
        self.ina = INA219(3.0, i2c_driver=self.i2c)
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_AUTO)

        self.ina._read_voltage_register = Mock(return_value=0xfa1)
        self.ina._read_configuration = Mock(return_value=0x199f)

        with self.assertRaisesRegex(DeviceRangeError, self.GAIN_RANGE_MSG):
            self.ina.current()
