from pypylon import pylon
import numpy as np
from libtiff import TIFF
from . import helper

import logging
logger = logging.getLogger(__name__)


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
        if ip is not None:
            info.SetIpAddress(ip)
        if serial_number is not None:
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
        for cam_property in self.PROPERTIES:
            
            is_available = getattr(cam.GetDeviceInfo(), 'Is' + cam_property + 'Available')
            if is_available():
                attr = getattr(cam.GetDeviceInfo(), 'Get' + cam_property)
                info[cam_property] = attr()
                
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

    def grab_one(self, convert = True):
    
        """grab one frame and return data as a numpy array"""

        logger.info("grab one frame")
        
        cam = self.get_camera()
        r = cam.GrabOne(self.TIME_OUT)
        if convert:
            converter = helper.get_image_converter()
            target_image = converter.Convert(r)
            y = target_image.GetArray()
        else:
            y = r.Array
            
        r.Release()
        return y

    def grab_n(self, n, frame_rate=None, convert=True):
    
        """grab n frames and return a numpy array of shape n x height x width"""

        info_text = "grabbing %d frames at %.1f fps" % (n, frame_rate) if frame_rate is not None \
            else "grabbing %d frames" % n

        logger.info(info_text)

        cam = self.get_camera()

        if frame_rate:
            helper.set_framerate(cam, frame_rate)
        else:
            helper.set_framerate(cam, None)

        if convert:
            converter = helper.get_image_converter()

        width = cam.Width.GetValue()
        height = cam.Height.GetValue()
        r = np.zeros([n, height, width])
        i = 0

        cam.StartGrabbingMax(n)
        while cam.IsGrabbing():

            grab_result = cam.RetrieveResult(self.TIME_OUT, pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grab_result.GrabSucceeded():
                if convert:
                    target_image = converter.Convert(grab_result)
                    r[i, :, :] = target_image.GetArray()
                else:
                    r[i, :, :] = grab_result.Array
                i += 1
            else:
                print("Error: ", grab_result.ErrorCode, grab_result.ErrorDescription)
            grab_result.Release()

        return r

    def grab_n_save(self, n, frame_rate, save_pattern, n_start=1, convert=True):
    
        """grab n frames and save them as tiff files according to save_pattern.
        
        Example:
        
        grab_n_save(200, 25, '/home/zheli/images/0722-%d.tiff', 1):
        """

        info_text = "grabbing and saving %d frames at %.1f fps" % (n, frame_rate) if frame_rate \
            else "grabbing and saving %d frames" % n

        logger.info(info_text)

        cam = self.get_camera()

        width = cam.Width.GetValue()
        height = cam.Height.GetValue()
        i = 0

        if frame_rate:
            helper.set_framerate(cam, frame_rate)
        else:
            helper.set_framerate(cam, None)

        if convert:
            converter = helper.get_image_converter()

        cam.StartGrabbingMax(n)
        while cam.IsGrabbing():

            grab_result = cam.RetrieveResult(self.TIME_OUT, pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grab_result.GrabSucceeded():
                if convert:
                    target_image = converter.Convert(grab_result)
                    r = target_image.GetArray()
                else:
                    r = grab_result.Array
                filename = save_pattern % (n_start + i)
                tif = TIFF.open(filename, 'w')
                tif.write_image(r)
                i += 1
                grab_result.Release()
            else:
                print("Error: ", grab_result.ErrorCode, grab_result.ErrorDescription)
                logger.error("Error: " + str(grab_result.ErrorCode) + str(grab_result.ErrorDescription))


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
