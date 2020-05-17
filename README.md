# PyBasler

A Python module for connecting Basler cameras and capturing images. This is a wrapper based on the official [pypylon](https://github.com/basler/pypylon) package.

It contains the following classes:
* `BaslerCamera`: a base class for Basler cameras
* `BaslerCameraArray`: a base class for Basler camera arrays
* `BaslerCameraManager`: a manager class, currently can be used to return a list of available cameras

## Example

```Python
>>> from basler.basler_camera import BaslerCamera
>>> from basler.helper import BaslerCameraManager
>>> import matplotlib.pyplot as plt
>>> BaslerCameraManager.get_camera_list_names()
['Basler piA1600-35gm (20717903)', 'Basler piA1600-35gm (21939024)']
>>> SERIAL_NUMBER = '21939024'
>>> cam = BaslerCamera(serial_number=SERIAL_NUMBER)
>>> cam.connect()
>>> frame = cam.grab_one()
>>> plt.imshow(frame, cmap='gray')
>>> plt.show()
>>> cam.disconnect()
```

## Prerequisites

* numpy
* [pypylon](https://github.com/basler/pypylon)

## Documentation

Full Documentation is available at [https://lizhe.me/pybasler-docs/](https://lizhe.me/pybasler-docs/).