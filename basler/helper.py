

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
