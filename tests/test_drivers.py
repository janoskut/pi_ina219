import sys
import logging
import unittest

from mock import Mock, patch

from ina219 import drivers


logger = logging.getLogger()
logger.level = logging.ERROR
logger.addHandler(logging.StreamHandler(sys.stdout))


class TestDrivers(unittest.TestCase):

    def setUp(self) -> None:
        sys.modules['smbus'] = Mock()
        sys.modules['smbus2'] = Mock()
        sys.modules['Adafruit_PureIO'] = Mock()
        sys.modules['Adafruit_PureIO.smbus'] = Mock()

    def tearDown(self) -> None:
        if 'smbus' in sys.modules:
            del sys.modules['smbus']
        if 'smbus2' in sys.modules:
            del sys.modules['smbus2']
        if 'Adafruit_PureIO' in sys.modules:
            del sys.modules['Adafruit_PureIO']
        if 'Adafruit_PureIO.smbus' in sys.modules:
            del sys.modules['Adafruit_PureIO.smbus']

    @patch('smbus.SMBus')
    def test_smbus_driver(self, smbus):

        driver = drivers.SmbusDriver.load(interface=123)
        driver.write(0xAB, 0xCD, b'\xaa\xbb\xcc\xdd')

        smbus.assert_called_with(123)

        instance = smbus.return_value

        instance.write_i2c_block_data.assert_called_with(
            0xAB, 0xCD, [0xaa, 0xbb, 0xcc, 0xdd])

        instance.read_i2c_block_data.return_value = [0xAB, 0xCD]
        read_unsigned = driver.read_word(0xBA, 0xDC, signed=False)
        self.assertEqual(read_unsigned, 0xABCD)

        instance.read_i2c_block_data.return_value = [0xAB, 0xCD]
        read_signed = driver.read_word(0xBA, 0xDC, signed=True)
        self.assertEqual(read_signed, -21555)

    @patch('smbus2.SMBus')
    def test_smbus2_driver(self, smbus):

        driver = drivers.Smbus2Driver.load(interface=123)
        driver.write(0xAB, 0xCD, b'\xaa\xbb\xcc\xdd')

        smbus.assert_called_with(123)

        instance = smbus.return_value

        instance.write_i2c_block_data.assert_called_with(
            0xAB, 0xCD, [0xaa, 0xbb, 0xcc, 0xdd])

        instance.read_i2c_block_data.return_value = [0xAB, 0xCD]
        read_unsigned = driver.read_word(0xBA, 0xDC, signed=False)
        self.assertEqual(read_unsigned, 0xABCD)

        instance.read_i2c_block_data.return_value = [0xAB, 0xCD]
        read_signed = driver.read_word(0xBA, 0xDC, signed=True)
        self.assertEqual(read_signed, -21555)

    @patch('Adafruit_PureIO.smbus.SMBus')
    def test_adafruit_driver(self, smbus):

        driver = drivers.AdafruitDriver.load(interface=123)
        driver.write(0xAB, 0xCD, b'\xaa\xbb\xcc\xdd')

        smbus.assert_called_with(123)

        instance = smbus.return_value

        instance.write_i2c_block_data.assert_called_with(
            0xAB, 0xCD, [0xaa, 0xbb, 0xcc, 0xdd])

        instance.read_i2c_block_data.return_value = [0xAB, 0xCD]
        read_unsigned = driver.read_word(0xBA, 0xDC, signed=False)
        self.assertEqual(read_unsigned, 0xABCD)

        instance.read_i2c_block_data.return_value = [0xAB, 0xCD]
        read_signed = driver.read_word(0xBA, 0xDC, signed=True)
        self.assertEqual(read_signed, -21555)

    def test_auto_driver(self):
        driver = drivers.auto(interface=321)
        self.assertEqual(driver.__class__, drivers.Smbus2Driver)

        del sys.modules['smbus2']
        driver = drivers.auto(interface=321)
        self.assertEqual(driver.__class__, drivers.SmbusDriver)

        del sys.modules['smbus']
        driver = drivers.auto(interface=321)
        self.assertEqual(driver.__class__, drivers.AdafruitDriver)

        del sys.modules['Adafruit_PureIO.smbus']
        exp_exc_msg = 'No compatible I2C module found'
        with self.assertRaisesRegex(ModuleNotFoundError, exp_exc_msg):
            driver = drivers.auto(interface=321)
