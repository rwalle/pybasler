import pypylon

FRAMERATE_EPISLON = 0.1

def set_framerate(cam, frame_rate=None):

    """
    set_framerate(framerate)

    it looks like the framerate set node can be either AcquisitionFrameRateAbs or AcquisitionFrameRate. So this function
    attempts to use both names before giving up
    """
    
    if frame_rate:

        cam.AcquisitionFrameRateEnable.SetValue(True)
        try:
            cam.AcquisitionFrameRateAbs.SetValue(frame_rate)
            real_fps = cam.ResultingFrameRateAbs.GetValue()
            if abs(frame_rate - real_fps) > FRAMERATE_EPISLON:
                raise RuntimeError("Cannot set framerate: resulting frame rate is too far from target framerate.")
                cam.AcquisitionFrameRateEnable.SetValue(False) # rollback
        except pypylon._genicam.LogicalErrorException:
            try:
                cam.AcquisitionFrameRate.SetValue(frame_rate)
                if abs(frame_rate - real_fps) > FRAMERATE_EPISLON:
                    raise RuntimeError("Cannot set framerate: resulting frame rate is too far from target framerate.")
                    cam.AcquisitionFrameRateEnable.SetValue(False) # rollback
            except pypylon._genicam.LogicalErrorException as e:
                print("cannot find the node for setting frame rate. giving up.")
                print(repr(e))
                cam.AcquisitionFrameRateEnable.SetValue(False)
            
    else:
    
        cam.AcquisitionFrameRateEnable.SetValue(False)

def get_image_converter():
    
    converter = pypylon.pylon.ImageFormatConverter()

    converter.OutputPixelFormat = pypylon.pylon.PixelType_Mono16

    converter.OutputBitAlignment = pypylon.pylon.OutputBitAlignment_MsbAligned
    
    return converter


def get_shift_bits(cam):

    """
    get_shift_bits(cam)
    
    return the number of bits to shift so that the most significant bit ('msb') is aligned

    recommend to use get_image_converter and convert image instead
    """

    bit_size = cam.PixelSize.GetValue()
    bit = int(bit_size[3:])  # bit_size are like 'Bpp8', 'Bpp12' and always start with 'Bpp'
    if bit < 8:
        return 8 - bit
    elif 8 < bit < 16:
        return 16 - bit
    else:
        return 0
