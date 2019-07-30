from pypylon import pylon
from pypylon import genicam
import numpy as np
from libtiff import TIFF

class BaslerCamera:

    """
    a generic class for connecting Basler cameras and capturing images.
    """

    TIME_OUT = 2000
    
    PROPERTIES = [
        'Address',
        'DeviceClass',
        'DeviceID',
        'FriendlyName',
        'FullName',
        'IpAddress',
        'ModelName',
        'SerialNumber',]
    
    def __init__(self, ip = None, serial_number = None):
        info = pylon.CDeviceInfo()
        if ip != None:
            info.SetIpAddress(ip)
        if serial_number != None:
            info.SetSerialNumber(serial_number)
        self.cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))

    def get_camera(self):
        try:
            cam = self.cam
        except AttributeError:
            print('camera not initialized')
            raise

        return cam
        
    def get_camera_info(self):
        cam = self.get_camera()
        info = {}
        for property in self.PROPERTIES:
            
            is_availble = getattr(cam.GetDeviceInfo(), 'Is' + property + 'Available')
            if is_availble():
                attr = getattr(cam.GetDeviceInfo(), 'Get' + property)
                info[property] = attr()
                
        return info
    
    def open(self):
        self.get_camera().Open()

    def close(self):
        self.get_camera().Close()

    def set_aoi(self, offset_x, offset_y, width, height):
        cam = self.get_camera()
        
        cam.Height.SetValue(height)
        cam.Width.SetValue(width)
        cam.OffsetX.SetValue(offset_x)
        cam.OffsetY.SetValue(offset_y)

    def grab_one(self):
    
        """grab one frame and return data as a numpy array"""
        
        cam = self.get_camera()
        r = cam.GrabOne(self.TIME_OUT)
        y = r.Array
        r.Release()
        return y

    def grab_n(self, n, fps = None):
    
        """grab n frames and return a numpy array of shape n x height x width"""
    
        cam = self.get_camera()

        if fps:
            cam.AcquisitionFrameRateEnable.SetValue(True)
            cam.AcquisitionFrameRate.SetValue(fps)
        else:
            cam.AcquisitionFrameRateEnable.SetValue(False)

        width = cam.Width.GetValue()
        height = cam.Height.GetValue()
        r = np.zeros([n, height, width])
        i = 0

        cam.StartGrabbingMax(n)
        while cam.IsGrabbing():

            grabResult = cam.RetrieveResult(self.TIME_OUT, pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grabResult.GrabSucceeded():
                r[i, :, :]= grabResult.Array
                i += 1
            else:
                print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
            grabResult.Release()

        return r

    def grab_n_save(self, n, fps, save_pattern, n_start = 1):
    
        """grab n frames and save them as tiff files according to save_pattern.
        
        Example:
        
        grab_n_save(200, 25, '/home/zheli/images/0722-%d.tiff', 1):
        """

        cam = self.get_camera()

        width = cam.Width.GetValue()
        height = cam.Height.GetValue()
        i = 0

        if fps:
            cam.AcquisitionFrameRateEnable.SetValue(True)
            cam.AcquisitionFrameRate.SetValue(fps)
        else:
            cam.AcquisitionFrameRateEnable.SetValue(False)

        cam.StartGrabbingMax(n)
        while cam.IsGrabbing():

            grabResult = cam.RetrieveResult(self.TIME_OUT, pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grabResult.GrabSucceeded():
                r = grabResult.Array
                filename = save_pattern % (n_start + i)
                tif = TIFF.open(filename, 'w')
                tif.write_image(r)
                i += 1
            else:
                print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)

            grabResult.Release()


def get_camera_list():

    """return a list of available cameras in the "friendly name" format containing serial numbers"""
    
    Tlfactory = pylon.TlFactory.GetInstance()
    devices = Tlfactory.EnumerateDevices()
    friendly_names = []
    for device in devices:
        friendly_names.append(device.GetFriendlyName())
    return friendly_names
    
def get_camera_list_full():

    """return a list of available cameras in the "full name" format containing addresses"""
    
    Tlfactory = pylon.TlFactory.GetInstance()
    devices = Tlfactory.EnumerateDevices()
    full_names = []
    for device in devices:
        full_names.append(device.GetFullName())
    return full_names