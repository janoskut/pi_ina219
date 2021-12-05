import sys
import logging
import unittest

from mock import Mock, patch

from ina219 import INA219, I2cDriver


logger = logging.getLogger()
logger.level = logging.ERROR
logger.addHandler(logging.StreamHandler(sys.stdout))


class TestConstructor(unittest.TestCase):

    def setUp(self):
        I2cDriver.register(Mock)  # make "Mock" a subclass of "I2cDriver"
        self.i2c = Mock()

    @patch('ina219.drivers')
    def test_old_interface(self, drivers):
        drivers.auto = Mock()

        self.ina = INA219(0.1)
        drivers.auto.assert_called_with(interface=1)

        # with busnum
        self.ina = INA219(0.1, busnum=2)
        drivers.auto.assert_called_with(interface=2)

    @patch('logging.getLogger')
    def test_new_interface_with_deprecated_busnum(self, logger):
        self.ina = INA219(0.1, busnum=0, i2c_driver=self.i2c)
        self.ina.logger.warning.assert_called()

    def test_default(self):
        self.ina = INA219(0.1, i2c_driver=self.i2c)
        self.assertEqual(self.ina._shunt_ohms, 0.1)
        self.assertIsNone(self.ina._max_expected_amps)
        self.assertIsNone(self.ina._gain)
        self.assertFalse(self.ina._auto_gain_enabled)
        self.assertAlmostEqual(self.ina._min_device_current_lsb, 6.25e-6, 2)

    def test_with_max_expected_amps(self):
        self.ina = INA219(0.1, 0.4, i2c_driver=self.i2c)
        self.assertEqual(self.ina._shunt_ohms, 0.1)
        self.assertEqual(self.ina._max_expected_amps, 0.4)

    def test_with_invalid_i2c_device_class(self):
        non_i2c_driver_instance = object()
        exp_exc_msg = 'I2C driver class must be a subclass of I2cDriver'
        with self.assertRaisesRegex(AssertionError, exp_exc_msg):
            self.ina = INA219(0x40, 0, i2c_driver=non_i2c_driver_instance)
