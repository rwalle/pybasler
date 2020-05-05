# PyBasler
A Python module for connecting Basler cameras. It contains the following classes:
* `BaslerCamera`: a base class for Basler cameras
* `BaslerCameraArray`: a base class for Basler camera arrays
* `BaslerPIA160035GM`, `BaslerAcA1920155um`: two concrete Basler camera classes. You are free to use them as examples and create your own classes
* `BaslerCameraFactory`: a factory that automatically creates camera objects based on model names
* `BaslerCameraManager`: a manager class, currently can be used to return a list of available cameras

## Example

```Python
>>> from basler.basler_camera import BaslerPIA160035GM, BaslerCameraManager
>>> import matplotlib.pyplot as plt
>>> BaslerCameraManager.get_camera_list_names()
['Basler piA1600-35gm (20717903)', 'Basler piA1600-35gm (21939024)']
>>> SERIAL_NUMBER = '21939024'
>>> cam = BaslerPIA160035GM(serial_number=SERIAL_NUMBER)
>>> cam.open()
>>> frame = cam.grab_one()
>>> plt.imshow(frame, cmap='gray')
>>> plt.show()
>>> cam.close()
```

## Prerequisites

* numpy
* [pypylon](https://github.com/basler/pypylon)

## Single Camera API reference

This section is a bit disorganized. Will update with a better documentation later.

### Initiate a single camera instance

`camera = BaslerCamera(ip=None, serial_number=None)`

Connect to a specific camera using its IP address (for GigE cameras) or serial number (generic). If left as None, that one that found first is used as the camera.

### Open/Close the camera for capture

`camera.connect()`

`camera.disconnect()`

### Grabbing

grab one frame

`frame = camera.grab_one()`

Grab N frames and return a matrix of N x height x width

`frames = camera.grab_many(n)`

Grab N frames and save to disk

`camera.grab_n_save(n, save_pattern, n_start=1)`

`save_pattern` contains exactly one `%d` for the numeric index.

Example:

`grab_n_save(200, 25, '/home/zheli/images/0722-%d.tiff', 1)`

### Get camera information

`camera.get_camera_info()`

returns a dictionary with keys `Address`, `DeviceClass`, `DeviceID`, `FriendlyName`, `FullName`, `IpAddress`, `ModelName`, and `SerialNumber`.

### Get camera dynamic range

`camera.get_dynamic_range()`

returns a tuple `(min, max)`

### Setting capture parameters

Set camera pixel format

`camera.set_pixel_format(pixel_format_string)`

`pixel_format_string` looks like `Mono12`, `Mono8`, and `Mono12Packed` etc., and varies from camera to camera. See camera documentation in the Basler software for details.

Set area of interest (AOI) for capture

`camera.set_aoi(self, aoi)`

`aoi` is a tuple: `(offset_x, offset_y, width, height)`

Enable digital shift of images using most significant bits (MSB)

`camera.set_converter(enabled)`

Set exposure time

`camera.set_exposure_time(exposure_time)`

This method is **NOT IMPLEMENTED** in the generic `BaslerCamera` class, as the exposure time is defined differently for different models. However, examples are given in `BaslerPIA160035GM` and `BaslerAcA1920155um`, and you are free to inherit the base class and implement your own method

Set frame rate

`camera.set_framerate(framerate)`

This method is **NOT IMPLEMENTED** in the generic `BaslerCamera` class, for the same reason as the exposure time. Similarly, camera gain setter is not provided.

### List all available cameras

return "friendly" names:

`BaslerCameraManager.get_camera_list_names()`

return full names:

`BaslerCameraManager.get_camera_list_fullname()`

return camera details, as a list of dictionaries where each dictionary contains `name`, `serial_number` and `model_name` of the camera.

`BaslerCameraManager.get_camera_list_dict()`

## Camera Array Reference

### Initiate a camera array

`array = BaslerCameraArray(devices_info)`

`devices_info` is a list of dictionaries, where each dictionary contains either the key `ip` or `serial_number` as two ways of identifying cameras.

### Get an individual camera from the array object

`camera = array.get_camera(camera_id)`

`camera_id` is the order in the `devices_info` at initialization. Same below.

### Set pixel format

... to be updated later