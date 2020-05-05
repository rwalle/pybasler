import unittest
from basler.basler_camera import BaslerCamera


class TestCamera(unittest.TestCase):

    SERIAL_NUMBER = '21939024'
    IP_ADDRESS = '192.168.0.2'

    def test_0_test_sn_connection(self):
    
        self.cam = BaslerCamera(serial_number=self.SERIAL_NUMBER)
        self.cam.connect()

        camera_info = self.cam.get_camera_info()
        serial_number = camera_info['SerialNumber']
        self.assertEqual(self.SERIAL_NUMBER, serial_number)
        
        self.cam.disconnect()
        
    def test_1_test_ipaddress_connection(self):

        self.cam = BaslerCamera(ip=self.IP_ADDRESS)
        self.cam.connect()

        camera_info = self.cam.get_camera_info()
        ip_address = camera_info['IpAddress']
        self.assertEqual(self.IP_ADDRESS, ip_address)
        
        self.cam.disconnect()

if __name__ == '__main__':
    unittest.main()