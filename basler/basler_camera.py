import pypylon
import pypylon.pylon
import numpy as np

class DeviceError(Exception):
    pass


class BaslerCamera():

    """
    a generic class for connecting Basler cameras and capturing images.
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
        """
        self.device = None
        self.device_info = pypylon.pylon.CDeviceInfo()
        if ip is not None:
            self.device_info.SetIpAddress(ip)
        if serial_number is not None:
            self.device_info.SetSerialNumber(serial_number)
        self.converter = None

    def get_device(self):
        if self.device is None:
            raise NameError('Not initialized')
        return self.device

    def connect(self):
        if self.device is None:
            self.device = pypylon.pylon.InstantCamera(pypylon.pylon.TlFactory.GetInstance().CreateFirstDevice(self.device_info))
        self.set_converter()
        self.get_device().Open()

    def disconnect(self):
        if self.get_device().IsOpen():
            self.get_device().Close()

    def __del__(self):
        self.converter = None
        # super(BaslerCamera, self).__del__()

    # ---------------------- camera settings -------------------------

    def set_aoi(self, aoi: tuple):
        
        offset_x, offset_y, width, height = aoi
        cam = self.get_device()
        
        cam.Height.SetValue(height)
        cam.Width.SetValue(width)
        cam.OffsetX.SetValue(offset_x)
        cam.OffsetY.SetValue(offset_y)

    def set_pixel_format(self, pixel_format_string: str):

        cam = self.get_device()
        cam.PixelFormat.SetValue(pixel_format_string)

    def set_converter(self, convert=True):

        if convert:
            self.converter = pypylon.pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pypylon.pylon.PixelType_Mono16
            self.converter.OutputBitAlignment = pypylon.pylon.OutputBitAlignment_MsbAligned
            
    def get_camera_info(self):
        cam = self.get_device()
        info = {}
        for cam_property in self._PROPERTIES:

            is_available = getattr(cam.GetDeviceInfo(), 'Is' + cam_property + 'Available')
            if is_available():
                attr = getattr(cam.GetDeviceInfo(), 'Get' + cam_property)
                info[cam_property] = attr()

        return info
        
    def get_dynamic_range(self):
        cam = self.get_device()
        dynamic_range = (cam.PixelDynamicRangeMin.GetValue(), cam.PixelDynamicRangeMax.GetValue())
        return dynamic_range

    def set_exposure_time(self, exposure_time: float):
        raise NotImplementedError

    def set_framerate(self, framerate: float=None):
        raise NotImplementedError

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

        cam = self.get_device()
        acquired_image = cam.GrabOne(self._TIME_OUT)
        result = self.post_processing(acquired_image).GetArray()
        acquired_image.Release()
        return result

    def grab_many(self, n: int):
    
        """grab n frames and return a numpy array of shape n x height x width"""

        cam = self.get_device()

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

    def grab_n_save(self, n: int, save_pattern: str, n_start:int=1):
    
        """grab n frames and save them as tiff files according to save_pattern.
        
        Example:
        
        grab_n_save(200, '/home/zheli/images/0722-%d.tiff')

        Images are saved as 0722-1.tiff, 0722-2.tif, ...
        """

        cam = self.get_device()

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


# -------------- Basler Camera Array ------------------------------

class BaslerCameraArray():

    _TIME_OUT = 2000

    def __init__(self, devices_info):

        self.camera_array = None
        
        self.device_info = []

        for device_info in devices_info:
            info = pypylon.pylon.CDeviceInfo()
            if 'ip' in device_info:
                info.SetIpAddress(device_info['ip'])
            if 'serial_number' in device_info:
                info.SetSerialNumber(device_info['serial_number'])
            self.device_info.append(info)

        self.converter = None

    def get_camera_array(self):
        if self.camera_array == None:
            raise NameError('Not initialized!')
        else:
            return self.camera_array

    def get_camera(self, cam_id: int):
        camera_array = self.get_camera_array()
        if (cam_id < 0) or (cam_id > camera_array.GetSize() - 1):
            raise ValueError('Wrong Camera ID')
        camera = camera_array[cam_id]
        return camera

    def set_converter(self, convert=True):

        if convert:
            self.converter = pypylon.pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pypylon.pylon.PixelType_Mono16
            self.converter.OutputBitAlignment = pypylon.pylon.OutputBitAlignment_MsbAligned

    def post_processing(self, grab_result):

        if self.converter is not None:
            target_image = self.converter.Convert(grab_result)
        else:
            target_image = pypylon.pylon.PylonImage()
            target_image.AttachGrabResultBuffer(grab_result)
        
        return target_image

    def set_pixel_format(self, id: int, pixel_format_string: str):

        camera = self.get_camera(id)
        camera.PixelFormat.SetValue(pixel_format_string)

    def connect(self):
        tlf = pypylon.pylon.TlFactory.GetInstance()
        num_devices = len(self.device_info)
        self.camera_array = pypylon.pylon.InstantCameraArray(num_devices)
        for idx, device_info in enumerate(self.device_info):
            self.camera_array[idx].Attach(tlf.CreateDevice(device_info))
        self.camera_array.Open()

    def disconnect(self):
        
        camera_array = self.get_camera_array()
        camera_array.Close()
        self.camera_array = None

    def set_framerate(self, id: int, framerate: float=None):

        camera = self.get_camera(id)
        if framerate:
            try:
                camera.AcquisitionFrameRateEnable.SetValue(True)
                camera.AcquisitionFrameRateAbs.SetValue(framerate)
            except pypylon._genicam.LogicalErrorException:
                try:
                    camera.AcquisitionFrameRateEnable.SetValue(True)
                    camera.AcquisitionFrameRateAbs.SetValue(framerate)
                except pypylon._genicam.LogicalErrorException:
                    raise RuntimeError(f'Unable to set framerate for camera {id}.') 
        else:
            camera.AcquisitionFrameRateEnable.SetValue(False)

    def set_exposure_time(self, id: int, exposure_time: float):

        camera = self.get_camera(id)
        try:
            camera.ExposureTime.SetValue(exposure_time * 1000)
        except pypylon._genicam.LogicalErrorException:
            try:
                camera.ExposureTimeAbs.SetValue(exposure_time * 1000)
            except pypylon._genicam.LogicalErrorException:
                raise RuntimeError(f'Unable to set exposure time for camera {id}.')

    def set_aoi(self, id: int, aoi: tuple):
        offset_x, offset_y, width, height = aoi

        camera = self.get_camera(id)
        
        camera.Height.SetValue(height)
        camera.Width.SetValue(width)
        camera.OffsetX.SetValue(offset_x)
        camera.OffsetY.SetValue(offset_y)
    
    def grab_one(self):

        camera_array = self.get_camera_array()

        size = camera_array.GetSize()

        result = []

        for i in range(size):
            grab_result = camera_array[i].GrabOne(self._TIME_OUT)
            image_array = self.post_processing(grab_result).GetArray()
            grab_result.Release()
            result.append(image_array)

        return result

    def grab_many(self, n: int):

        camera_array = self.get_camera_array()

        size = camera_array.GetSize()

        result = []
        frames_captured = np.zeros(size, dtype=int)

        for i in range(size): # pre allocate array memory
            cam = camera_array[i]

            width = cam.Width.GetValue()
            height = cam.Height.GetValue()
            r = np.zeros([n, height, width])
            result.append(r)

        camera_array.StartGrabbing()

        while True:

            if (not camera_array.IsGrabbing()) or np.all(frames_captured >= n):
                break
        
            grab_result = camera_array.RetrieveResult(self._TIME_OUT, pypylon.pylon.TimeoutHandling_ThrowException)
            camera_no = grab_result.GetCameraContext()
            image_array = self.post_processing(grab_result).GetArray()
            
            result[camera_no][frames_captured[camera_no], :, :] = image_array
            frames_captured[camera_no] += 1

        camera_array.StopGrabbing()

        return result

    def grab_n_save(self, n: int, save_pattern: list, n_start: list=None):

        camera_array = self.get_camera_array()

        size = camera_array.GetSize()

        frames_captured = np.zeros(size, dtype=int)
        if n_start is None:
            n_start = np.ones(size, dtype=int)

        camera_array.StartGrabbing()

        while True:

            if (not camera_array.IsGrabbing()) or np.all(frames_captured >= n):
                break
        
            grab_result = camera_array.RetrieveResult(self._TIME_OUT, pypylon.pylon.TimeoutHandling_ThrowException)
            camera_no = grab_result.GetCameraContext()
            
            image = self.post_processing(grab_result)
            
            image = pypylon.pylon.PylonImage(image)

            filename = save_pattern[camera_no] % (n_start[camera_no] + frames_captured[camera_no])

            image.Save(pypylon.pylon.ImageFileFormat_Tiff, filename)
            image.Release()
                
            grab_result.Release()

            frames_captured[camera_no] += 1

        camera_array.StopGrabbing()

# -------------- Concrete Basler Cameras --------------------------


class BaslerPIA160035GM(BaslerCamera):

    """
    For Basler pia1600-35gm GigE camera
    """

    _PIXEL_FORMAT = "Mono12Packed"
    _PACKET_SIZE = 9000

    def connect(self):

        super().connect()

        cam = self.get_device()
        cam.GevSCPSPacketSize.SetValue(self._PACKET_SIZE)
        cam.PixelFormat.SetValue(self._PIXEL_FORMAT)

    def set_exposure_time(self, exposure_time: float):

        cam = self.get_device()
        cam.ExposureTimeAbs.SetValue(exposure_time * 1000)

    def set_framerate(self, framerate: float=None):

        cam = self.get_device()
        if framerate:
            cam.AcquisitionFrameRateEnable.SetValue(True)
            cam.AcquisitionFrameRateAbs.SetValue(framerate)
        else:
            cam.AcquisitionFrameRateEnable.SetValue(False)


class BaslerAcA1920155um(BaslerCamera):

    """
    For Basler acA1920-155um USB3 camera
    """

    _PIXEL_FORMAT = "Mono12"

    def connect(self):

        super().connect()

        cam = self.get_device()
        cam.PixelFormat.SetValue(self._PIXEL_FORMAT)

    def set_exposure_time(self, exposure_time: float):

        cam = self.get_device()
        cam.ExposureTime.SetValue(exposure_time * 1000)

    def set_framerate(self, framerate: float=None):

        cam = self.get_device()
        if framerate:
            cam.AcquisitionFrameRateEnable.SetValue(True)
            cam.AcquisitionFrameRate.SetValue(framerate)
        else:
            cam.AcquisitionFrameRateEnable.SetValue(False)

    def set_gain(self, gain):

        cam = self.get_device()
        cam.Gain.SetValue(gain)


# ------------------ Camera manager and factory -----------------


class BaslerCameraFactory:

    @staticmethod
    def get_camera_instance_from_model_name(model_name: str, **args) -> BaslerCamera:
        if model_name == 'acA1920-155um':
            return BaslerAcA1920155um(**args)
        elif model_name == 'piA1600-35gm':
            return BaslerPIA160035GM(**args)
        else:
            raise KeyError("Unknown model name. Edit basler_camera.py to add new cameras.")


class BaslerCameraManager:

    @staticmethod
    def get_camera_list_names() -> list:

        """return a list of available cameras in the "friendly name" format containing serial numbers"""

        devices = pypylon.pylon.TlFactory.GetInstance().EnumerateDevices()
        friendly_names = []
        for device in devices:
            friendly_names.append(device.GetFriendlyName())
        return friendly_names

    @staticmethod
    def get_camera_list_dict() -> list:

        devices = pypylon.pylon.TlFactory.GetInstance().EnumerateDevices()
        dct = []
        for device in devices:
            dct.append({'name': device.GetFriendlyName(),
                        'serial_number': device.GetSerialNumber(),
                        'model_name': device.GetModelName()})
        return dct

    @staticmethod
    def get_camera_list_fullname() -> list:

        """return a list of available cameras in the "full name" format containing addresses"""

        devices = pypylon.pylon.TlFactory.GetInstance().EnumerateDevices()
        full_names = []
        for device in devices:
            full_names.append(device.GetFullName())
        return full_names
