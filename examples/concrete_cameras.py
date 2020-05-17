from basler.basler_camera import BaslerCamera


class BaslerPIA160035GM(BaslerCamera):

    """
    For Basler pia1600-35gm GigE camera
    """

    _PIXEL_FORMAT = "Mono12Packed"
    _PACKET_SIZE = 9000

    def connect(self):

        super().connect()

        cam = self._get_device()
        cam.GevSCPSPacketSize.SetValue(self._PACKET_SIZE)
        cam.PixelFormat.SetValue(self._PIXEL_FORMAT)

    def set_exposure_time(self, exposure_time: float):

        cam = self._get_device()
        cam.ExposureTimeAbs.SetValue(exposure_time * 1000)

    def set_acquisition_framerate(self, framerate: float=None):

        cam = self._get_device()
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

        cam = self._get_device()
        cam.PixelFormat.SetValue(self._PIXEL_FORMAT)

    def set_exposure_time(self, exposure_time: float):

        cam = self._get_device()
        cam.ExposureTime.SetValue(exposure_time * 1000)

    def set_acquisition_framerate(self, framerate: float=None):

        cam = self._get_device()
        if framerate:
            cam.AcquisitionFrameRateEnable.SetValue(True)
            cam.AcquisitionFrameRate.SetValue(framerate)
        else:
            cam.AcquisitionFrameRateEnable.SetValue(False)

    def set_gain(self, gain):

        cam = self._get_device()
        cam.Gain.SetValue(gain)
