# PyBasler
A Python module for connecting basler cameras.

## Example

```Python
>>> import basler.basler as basler
>>> import matplotlib.pyplot as plt
>>> basler.get_camera_list()
['Basler piA1600-35gm (20717903)', 'Basler piA1600-35gm (21939024)']
>>> SERIAL_NUMBER = '21939024'
>>> cam = basler.BaslerCamera(serial_number = SERIAL_NUMBER)
>>> cam.open()
>>> frame = cam.grab_one()
>>> plt.imshow(frame, cmap='gray')
>>> plt.show()
>>> cam.close()
```

## Prerequisites

* numpy
* [pypylon](https://github.com/basler/pypylon)
* [pylibtiff](https://github.com/pearu/pylibtiff)

## API reference

### list all available cameras

return "friendly" names:

`basler.get_camera_list()`

return full names:

`basler.get_camera_list_full()`

### initiate an instance

`camera = BaslerCamera(ip = None, serial_number = None)`
Connect to a specific camera using its IP address (for GigE cameras) or serial number (generic). If left as None, that one that found first is used as the camera.

### open the camera for capture

`camera.open()`

### close the camera

`camera.close()`

### get camera information

`camera.get_camera_info()`

### set area of interest (AOI) for capture

`camera.set_aoi(self, offset_x, offset_y, width, height)`

### grab one frame

`frame = camera.grab_one()`

### grab N frames and return a matrix of N x height x width

`frames = camera.grab_n(n, fps = None)`

### grab N frames and save to disk

`camera.grab_n_save(n, fps, save_pattern, n_start=1)`

`save_pattern` contains exactly one `%d` for the numeric index.

Example:

`grab_n_save(200, 25, '/home/zheli/images/0722-%d.tiff', 1)`
