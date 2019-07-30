import unittest
from basler.basler import BaslerCamera


class TestCamera(unittest.TestCase):

    SERIAL_NUMBER = '21939024'
    IP_ADDRESS = '192.168.0.2'

    def test_0_test_sn_connection(self):
    
        self.cam = BaslerCamera(serial_number = self.SERIAL_NUMBER)
        self.cam.open()

        camera_info = self.cam.get_camera_info()
        serial_number = camera_info['SerialNumber']
        self.assertEqual(self.SERIAL_NUMBER, serial_number)
        
        self.cam.close()
        
    def test_1_test_ipaddress_connection(self):

        self.cam = BaslerCamera(ip = self.IP_ADDRESS)
        self.cam.open()

        camera_info = self.cam.get_camera_info()
        ip_address = camera_info['IpAddress']
        self.assertEqual(self.IP_ADDRESS, ip_address)
        
        self.cam.close()

if __name__ == '__main__':
    unittest.main()