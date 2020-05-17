from basler.basler_camera_array import BaslerCameraArray

CAM_CAPTURE_N = 100

CAM0_SN = '23060909'
CAM0_CAPTURE_SAVE_PATTERN = r'E:\test\cam0\basic-%d.tiff'  # Don't miss the leading `r`!
CAM0_AOI = (0, 0, 800, 800)  # area of interest
CAM0_PIXEL_FORMAT = 'Mono12'
CAM0_EXPOSURE_TIME = 10
CAM0_GAIN = 0
CAM0_FRAMERATE = 25

CAM1_SN = '23367990'
CAM1_CAPTURE_SAVE_PATTERN = r'E:\test\cam1\basic-%d.tiff'  # Don't miss the leading `r`!
CAM1_AOI = (0, 0, 800, 800)  # area of interest
CAM1_PIXEL_FORMAT = 'Mono12'
CAM1_EXPOSURE_TIME = 10
CAM1_GAIN = 0
CAM1_FRAMERATE = 25

if __name__ == '__main__':
    cam_array = BaslerCameraArray([{'serial_number': CAM0_SN}, {'serial_number': CAM1_SN}])

    # initialize

    cam_array.connect()

    cam_array.set_exposure_time(0, CAM0_EXPOSURE_TIME)
    cam_array.set_exposure_time(1, CAM1_EXPOSURE_TIME)
    cam_array.set_acquisition_framerate(0, CAM0_FRAMERATE)
    cam_array.set_acquisition_framerate(1, CAM1_FRAMERATE)
    cam_array.set_pixel_format(0, CAM0_PIXEL_FORMAT)
    cam_array.set_pixel_format(1, CAM0_PIXEL_FORMAT)
    cam_array.set_aoi(0, CAM0_AOI)
    cam_array.set_aoi(1, CAM1_AOI)

    # data acquisition

    cam_array.grab_n_save(CAM_CAPTURE_N, [CAM0_CAPTURE_SAVE_PATTERN, CAM1_CAPTURE_SAVE_PATTERN])

    # clean up

    cam_array.disconnect()
