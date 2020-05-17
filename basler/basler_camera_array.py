import numpy as np
from .basler_camera import BaslerCamera

class BaslerCameraArray:

    """
    A class for basler camera array. Useful for capturing from multiple cameras simultaneously.
    If the task requires high synchronization, using hardware synchronization is preferred.
    """

    _TIME_OUT = 2000

    def __init__(self, devices_info):

        """The constructor of the array.
        
        :param devices_info: a list of camera device info stored as dictionaries that has IP address
        or serial number.

        Examples:
        devices_info = [{'serial_number': '21939024'}, {'ip': '192.168.0.31'}]
        """

        self._camera_array = None
        self._device_info_objects = []
        self._converter = None

        for device_info in devices_info:
            info = pypylon.pylon.CDeviceInfo()
            if 'ip' in device_info:
                info.SetIpAddress(device_info['ip'])
            if 'serial_number' in device_info:
                info.SetSerialNumber(device_info['serial_number'])
            self._device_info_objects.append(info)

    def __get_camera_array(self):
        if self._camera_array is None:
            raise NameError('Not initialized!')
        else:
            return self._camera_array

    def __get_camera_by_id(self, cam_id: int):
        """get individual camera instance
        :param cam_id: camera ID, determined by the order of appearance in devices_info at initialization
        """
        camera_array = self.__get_camera_array()
        if (cam_id < 0) or (cam_id > camera_array.GetSize() - 1):
            raise ValueError('Wrong Camera ID')
        camera = camera_array[cam_id]
        return camera

    def connect(self):
        tlf = pypylon.pylon.TlFactory.GetInstance()
        num_devices = len(self._device_info_objects)
        self._camera_array = pypylon.pylon.InstantCameraArray(num_devices)
        for idx, device_info in enumerate(self._device_info_objects):
            self._camera_array[idx].Attach(tlf.CreateDevice(device_info))
        self._camera_array.Open()

    def disconnect(self):
        
        camera_array = self.__get_camera_array()
        camera_array.Close()
        self._camera_array = None

    # ----------------------- getter -----------------------------------

    def get_aoi(self, cam_id:int):
        """return the area of interest (AOI) of a certain camera
        :param cam_id: camera ID
        :return: a tuple of (offset_x, offset_y, width, height)
        """
        cam = self.__get_camera_by_id(cam_id)
        aoi = BaslerCamera.get_aoi_helper(cam)
        return aoi

    def get_exposure_time(self, cam_id:int):
        """return the exposure time of a certain camera in millisecond (ms).
        :param cam_id: camera ID
        """
        cam = self.__get_camera_by_id(cam_id)
        exposure_time = BaslerCamera.get_exposure_time(cam)
        return exposure_time

    def get_resulting_framerate(self, cam_id:int):
        """return the resulting framerate of a certain camera.
        :param cam_id: camera ID
        """
        cam = self.__get_camera_by_id(cam_id)
        framerate = BaslerCamera.get_resulting_framerate(cam)
        return framerate

    # ----------------------- setter -----------------------------------

    def set_converter(self, convert=True):

         """when saving TIFF files, always use a 16-bit format with the most significant bit (MSB)
        aligned.
        :param convert: a boolean
        """

        if convert:
            self._converter = pypylon.pylon.ImageFormatConverter()
            self._converter.OutputPixelFormat = pypylon.pylon.PixelType_Mono16
            self._converter.OutputBitAlignment = pypylon.pylon.OutputBitAlignment_MsbAligned
        else:
            self._converter = None

    def set_pixel_format(self, cam_id: int, pixel_format_string: str):

        """set acquisition pixel format for the camera.

        :param cam_id: camera id
        :param pixel_format_string: a pixel format string, like 'Mono8', 'Mono12', 'Mono12Packed'.
        Allowed values vary from camera to camera.
        Refer to camera documentation in the Pylon software for details.
        """

        cam = self.__get_camera_by_id(cam_id)
        cam.PixelFormat.SetValue(pixel_format_string)

    def set_acquisition_framerate(self, cam_id: int, framerate: float=None):

        """set the acquisition frame rates for a certain camera.

        :param cam_id: camera ID.
        :param framerate: frame rate.
        :type cam_id: int
        :type framerate: float

        See the `set_acquisition_framerate` of the `BaslerCamera class` for details.
        """

        cam = self.__get_camera_by_id(cam_id)
        BaslerCamera.set_acquisition_framerate_helper(cam, framerate)

    def set_exposure_time(self, cam_id: int, exposure_time: float):

        """set exposure time for a certain camera.

        :param cam_id: camera ID.
        :param exposure_time: exposure time.
        :type cam_id: int
        :type exposure_time: float

        See the `set_exposure_time` of `BaslerCamera` class for details. 
        """

        cam = self.__get_camera_by_id(cam_id)
        BaslerCamera.set_exposure_time_helper(cam, exposure_time)

    def set_aoi(self, cam_id: int, aoi: tuple):

        """set the area of interest (AOI) of the camera.
        :param cam_id: camera ID
        :param aoi: a tuple: (offset_x, offset_y, width, height)
        """

        cam = self.__get_camera_by_id(cam_id)
        
        BaslerCamera.set_aoi_helper(cam, aoi)

    # ----------------------- helper -----------------------------------

    def post_processing(self, grab_result):

        if self._converter is not None:
            target_image = self._converter.Convert(grab_result)
        else:
            target_image = pypylon.pylon.PylonImage()
            target_image.AttachGrabResultBuffer(grab_result)
        
        return target_image

    # --------------------------- grabbing -----------------------------
    
    def grab_one(self):

        """grab one frame from each camera as a list of numpy arrays"""

        camera_array = self.__get_camera_array()

        size = camera_array.GetSize()

        result = []

        for i in range(size):
            grab_result = camera_array[i].GrabOne(self._TIME_OUT)
            image_array = self.post_processing(grab_result).GetArray()
            grab_result.Release()
            result.append(image_array)

        return result

    def grab_many(self, n: int):

        """grab n frames from each camera, and return a list of numpy arrays of shape `(n, height_i, width_i)`
        where `height_i` and `width_i` is the height and width of the i-th camera

        :param n: the number of frames
        """

        camera_array = self.__get_camera_array()

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
    
        r"""grab n frames and save them sequentially as TIFF files

        :param n: the number of frames to grab for each camera
        :param save_patterns: a list of strings where each contains one single '%d' as the number.
        :param n_start: a list of integers indicating the start number of the filename
        
        Example:
        
        grab_n_save(200, ['/home/zhe/data/cam0-%d.tiff', '/home/zhe/data/cam1-%d.tiff'], [3, 5])

        Images are saved as `cam0-3.tiff`, `cam0-4.tiff`, ... for camera 0,
        and `cam1-5.tiff`, `cam1-6.tiff`, ... for camera 1 
        """

        camera_array = self.__get_camera_array()

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