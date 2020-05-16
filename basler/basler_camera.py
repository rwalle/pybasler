import pypylon
import pypylon.pylon
import numpy as np

class DeviceError(Exception):
    pass


class BaslerCamera():

    """
    A generic class for connecting Basler cameras and capturing images.
    """

    _TIME_OUT = 2000
    
    _PROPERTIES = [
        'Address',
        'DeviceClass',
        'DeviceID',
        'FriendlyName',
        'FullName',
        'IpAddress',
        'ModelName',
        'SerialNumber',]

    def __init__(self, ip: str=None, serial_number: str=None):
        """The constructor looks for the camera by IP address or serial number (or both). If neither is specified,
        the first device is created.
        
        :param ip: IP address
        :param serial_number: serial number
        """
        self._device = None
        self._device_info = pypylon.pylon.CDeviceInfo()
        if ip is not None:
            self._device_info.SetIpAddress(ip)
        if serial_number is not None:
            self._device_info.SetSerialNumber(serial_number)
        self.converter = None

    def __get_device(self):
        if self._device is None:
            raise NameError('Not initialized')
        return self._device

    def connect(self):
        if self._device is None:
            self._device = pypylon.pylon.InstantCamera(pypylon.pylon.TlFactory.GetInstance().CreateFirstDevice(self._device_info))
        self.set_converter()
        self.__get_device().Open()

    def disconnect(self):
        if self.__get_device().IsOpen():
            self.__get_device().Close()
        self._device = None

    def __del__(self):
        self.converter = None

    # ----------------------- getter -----------------------------------
            
    def get_camera_info(self):

        """return a dictionary of a few properties of the camera, including
        `Address`, `DeviceClass`, `DeviceID`, `FriendlyName`, `FullName`, `IpAddress`, `ModelName`,
        `SerialNumber`
        """
        cam = self.__get_device()
        info = {}
        for cam_property in self._PROPERTIES:

            is_available = getattr(cam.GetDeviceInfo(), 'Is' + cam_property + 'Available')
            if is_available():
                attr = getattr(cam.GetDeviceInfo(), 'Get' + cam_property)
                info[cam_property] = attr()

        return info
        
    def get_dynamic_range(self):
        """return the dynamic range of the image (affected by image format)
        :return: a tuple: (min_value, max_value)
        """
        cam = self.__get_device()
        dynamic_range = (cam.PixelDynamicRangeMin.GetValue(), cam.PixelDynamicRangeMax.GetValue())
        return dynamic_range

    def get_aoi(self):

        """return the area of interest (AOI) of the camera
        :return: a tuple: (offset_x, offset_y, width, height)
        """

        cam = self.__get_device()
        return BaslerCamera.get_aoi_helper(cam)

    @staticmethod
    def get_aoi_helper(cam):
        
        aoi = (cam.Height.GetValue(),
            cam.Width.GetValue(),
            cam.OffsetX.GetValue(),
            cam.OffsetY.GetValue())
        return aoi


    def get_exposure_time(self):
        """get the exposure time in millisecond (ms)"""
        cam = self.__get_device()
        exposure_time = BaslerCamera.get_exposure_time_helper(cam)
        return exposure_time

    @staticmethod
    def get_exposure_time_helper(cam):
        
        try:
            exposure_time = camera.ExposureTime.GetValue() / 1000
        except pypylon._genicam.LogicalErrorException:
            try:
                exposure_time = camera.ExposureTimeAbs.GetValue() / 1000
            except pypylon._genicam.LogicalErrorException:
                raise RuntimeError(f'Unable to set exposure time.')
        return exposure_time

    def get_resulting_framerate(self):
        """get the resulting frame rate. If frame rate control is not enabled, return None"""

        cam = self.__get_device()
        resulting_framerate = BaslerCamera.get_resulting_framerate_helper(cam)
        return resulting_framerate

    @staticmethod
    def get_resulting_framerate_helper(cam):

        framrate_control_enabled = cam.AcquisitionFrameRateEnable.GetValue()
        if not framrate_control_enabled:
            return None
        try:
            resulting_framerate = cam.ResultingFrameRateAbs.GetValue()
        except pypylon._genicam.LogicalErrorException:
            try:
                resulting_framerate = cam.ResultingFrameRate.GetValue()
            except pypylon._genicam.LogicalErrorException as e:
                raise RuntimeError("Unable to get the resulting framerate")

        return resulting_framerate

    # ----------------------- setter -----------------------------------

    def set_aoi(self, aoi:tuple):
        """set the area of interest (AOI) of the camera.
        :param aoi: a tuple: (offset_x, offset_y, width, height)
        """
        cam = self.__get_device()
        BaslerCamera.set_aoi_helper(cam, aoi)

    @staticmethod
    def set_aoi_helper(cam, aoi: tuple):

        offset_x, offset_y, width, height = aoi
        
        cam.Height.SetValue(height)
        cam.Width.SetValue(width)
        cam.OffsetX.SetValue(offset_x)
        cam.OffsetY.SetValue(offset_y)

    def set_pixel_format(self, pixel_format_string: str):

        """set acquisition pixel format for the camera.

        :param pixel_format_string: a pixel format string, like 'Mono8', 'Mono12', 'Mono12Packed'.
        Allowed values vary from camera to camera.
        Refer to camera documentation in the Pylon software for details.
        """

        cam = self.__get_device()
        cam.PixelFormat.SetValue(pixel_format_string)

    def set_converter(self, convert=True):

        """when saving TIFF files, always use a 16-bit format with the most significant bit (MSB)
        aligned.
        :param convert: a boolean
        """

        if convert:
            self.converter = pypylon.pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pypylon.pylon.PixelType_Mono16
            self.converter.OutputBitAlignment = pypylon.pylon.OutputBitAlignment_MsbAligned
        else:
            self.converter = None

    def set_exposure_time(self, exposure_time: float):

        """set exposure time for the camera.

        :param exposure_time: the exposure time, with unit in millisecond (ms).
        """

        cam = self.__get_device()
        BaslerCamera.set_exposure_time_helper(cam, exposure_time)

    @staticmethod
    def set_exposure_time_helper(cam, exposure_time: float):
        """A helper method for `set_exposure_time`

        This method will attempt to change `ExposureTime` property and then `ExposureTimeAbs`
        (as the property name varies from camera to camera). If no property is found,
        this method throws an error.
        """
        
        try:
            cam.ExposureTime.SetValue(exposure_time * 1000)
        except pypylon._genicam.LogicalErrorException:
            try:
                cam.ExposureTimeAbs.SetValue(exposure_time * 1000)
            except pypylon._genicam.LogicalErrorException:
                raise RuntimeError(f'Unable to set exposure time.')

    def set_acquisition_framerate(self, framerate: float=None):
        """set the acquisition frame rate for the camera.

        :param framerate: acquisition framerate

        The resulting (i.e. actural) framerate depends on a number of factors
        \(see the official [Basler Documentation] (https://docs.baslerweb.com/resulting-frame-rate.html)\)
        and may not equal the "acquisition frame rate" here.
        """
        cam = self.__get_device()
        BaslerCamera.set_acquisition_framerate_helper(cam, framerate)

    @staticmethod
    def set_acquisition_framerate_helper(cam, framerate: float=None):

        """A helper method for `set_acquisition_framerate`

        This method will attempt to change `AcquisitionFrameRate` property and then `AcquisitionFrameRateAbs`
        (as the property name varies from camera to camera). If no property is found,
        this method throws an error.
        If framerate is not specified or `None`, framerate control will be disabled.
        """
       
        if framerate:
            try:
                cam.AcquisitionFrameRateEnable.SetValue(True)
                cam.AcquisitionFrameRate.SetValue(framerate)
            except pypylon._genicam.LogicalErrorException:
                try:
                    cam.AcquisitionFrameRateEnable.SetValue(True)
                    cam.AcquisitionFrameRateAbs.SetValue(framerate)
                except pypylon._genicam.LogicalErrorException:
                    raise RuntimeError(f'Unable to set frame rate.') 
        else:
            cam.AcquisitionFrameRateEnable.SetValue(False)

    # ----------------------- helper -----------------------------------

    def post_processing(self, grab_result):

        if self.converter is not None:
            target_image = self.converter.Convert(grab_result)
        else:
            target_image = pypylon.pylon.PylonImage()
            target_image.AttachGrabResultBuffer(grab_result)
        
        return target_image

    # --------------------------- grabbing -----------------------------

    def grab_one(self):
    
        """grab one frame and return data as a numpy array"""

        cam = self.__get_device()
        acquired_image = cam.GrabOne(self._TIME_OUT)
        result = self.post_processing(acquired_image).GetArray()
        acquired_image.Release()
        return result

    def grab_many(self, n: int):
    
        """grab n frames and return a numpy array of shape (n, height, width)
        :param n: the number of frames
        """

        cam = self.__get_device()

        width = cam.Width.GetValue()
        height = cam.Height.GetValue()
        r = np.zeros([n, height, width])
        i = 0

        cam.StartGrabbingMax(n)
        while cam.IsGrabbing():

            grab_result = cam.RetrieveResult(self._TIME_OUT, pypylon.pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grab_result.GrabSucceeded():
                r[i, :, :] = self.post_processing(grab_result).GetArray()
                i += 1
            else:
                raise DeviceError("Error when grabbing images: " +
                                  str(grab_result.ErrorCode) + str(grab_result.ErrorDescription))
            grab_result.Release()

        return r

    def grab_n_save(self, n: int, save_pattern: str, n_start:int = 1):
    
        r"""grab n frames and save them sequentially as TIFF files according to save_pattern.

        :param n: the number of frames to grab
        :param save_pattern: a string that contains one single '%d' as the number.

        Windows - r'D:\20200212Z\002\002-%d.tiff' (Don't miss the leading 'r' which stands for 'raw' string; alternatively,
        use double backslash, e.g. 'D:\\20200212Z\\002\\002-%d.tiff')
        Linux - '/home/zheli/002/002-%d.tiff'
        
        :param n_start: the starting number or the sequence; default is 1
        
        Example:
        
        grab_n_save(200, '/home/zheli/images/0722-%d.tiff')

        Images are saved as 0722-1.tiff, 0722-2.tif, ...
        """

        cam = self.__get_device()

        width = cam.Width.GetValue()
        height = cam.Height.GetValue()
        i = 0

        cam.StartGrabbingMax(n)

        while cam.IsGrabbing():

            grab_result = cam.RetrieveResult(self._TIME_OUT, pypylon.pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grab_result.GrabSucceeded():

                filename = save_pattern % (n_start + i)
                i += 1

                r = self.post_processing(grab_result)
                
                img = pypylon.pylon.PylonImage(r)
                img.Save(pypylon.pylon.ImageFileFormat_Tiff, filename)
                img.Release()
                
                grab_result.Release()
            else:
                raise DeviceError("Error when grabbing images: " +
                                  str(grab_result.ErrorCode) + str(grab_result.ErrorDescription))
