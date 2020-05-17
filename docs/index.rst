.. PyBasler documentation master file, created by


Welcome to PyBasler's documentation!
====================================


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   basler_camera.md
   basler_camera_array.md
   helper.md
   
Quick Example
=============

.. code-block:: Python

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

API References
==============

* :class:`basler.basler_camera.BaslerCamera`
* :class:`basler.basler_camera_array.BaslerCameraArray`
* :class:`basler.helper.BaslerCameraManager`


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
