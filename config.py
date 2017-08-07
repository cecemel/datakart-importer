import datetime


def get_config(remote=False, sensor_data=False):
    """
    we assume
    id poszyx tag: 0x6858
    remote device: 0x6166
    """
    assert not (remote and sensor_data), "Currently remote and sensor data are mutally exclusive"

    basic_config = {"start_time": datetime.datetime.utcnow().isoformat(),
                    "anchors": [
                        {"label": "0x613e", "type": 1, "coordinates": {"x-value": 13292, "y-value": 11808, "z-value": 2000}},
                        {"label": "0x6107", "type": 1, "coordinates": {"x-value": 10751, "y-value": 0, "z-value": 2000}},
                        {"label": "0x6166", "type": 1, "coordinates": {"x-value": 0, "y-value": 0, "z-value": 2000}},
                        {"label": "0x6136", "type": 1, "coordinates": {"x-value": 4362, "y-value": 13902, "z-value": 2000}}
                    ],
                    "moving_device_height": 600,
                }

    if sensor_data:
        basic_config["sensor_data"] = True
        return basic_config

    if remote:
        basic_config["anchors"][2]["label"] = "0x6858"
        basic_config["anchors"][2]["type"] = 0
        basic_config["remote_device"] = "0x6166"
        return basic_config

    return basic_config



