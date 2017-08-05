from config import get_config
from utils import eprint, hex_string_to_hex
from pypozyx import POZYX_POS_ALG_UWB_ONLY, POZYX_2_5D, PozyxSerial, POZYX_3D, POZYX_POS_ALG_TRACKING
from localize import get_serial_ports, SimpleUDPClient, DeviceCoordinates, ReadyToLocalize, Coordinates
from services import queue_reader, \
    start_daemon_process, store_tracking_session_location_element, get_queue, get_http_session, get_session_data, \
    store_session_meta_data
from sensor_data import Orientation3D

from stats import print_stats
import datetime


def cli(queue):
    input("Press Enter to stop...")
    queue.put("EXIT")


def setup_poszyx(config_data):
    # TODO: clean out
    # shortcut to not have to find out the port yourself
    serial_port = get_serial_ports()[1].device

    remote_id = config_data.get("remote_device")

    # TODO: still not sure what it does
    # use_processing = True             # enable to send position data through OSC
    # ip = "127.0.0.1"                   # IP for the OSC UDP
    # network_port = 8888                # network port for the OSC UDP
    # osc_udp_client = None
    # if use_processing:
    #     osc_udp_client = SimpleUDPClient(ip, network_port)

    anchors = []

    for anchor in config_data["anchors"]:
        # necessary data for calibration, change the IDs and coordinates yourself
        device_coordinates = DeviceCoordinates(hex_string_to_hex(anchor["label"]),
                                               anchor["type"],
                                               Coordinates(anchor["coordinates"]["x-value"],
                                                           anchor["coordinates"]["y-value"],
                                                           anchor["coordinates"]["z-value"]))
        anchors.append(device_coordinates)

    # TODO check which algorithm is BEST
    algorithm = POZYX_POS_ALG_TRACKING  # positioning algorithm to use
    dimension = POZYX_3D              # positioning dimension

    #algorithm = POZYX_POS_ALG_UWB_ONLY  # positioning algorithm to use
    #dimension = POZYX_2_5D

    # TODO check what is needed
    height = config_data["moving_device_height"]   # height of device, required in 2.5D positioning


    # setup
    pozyx = PozyxSerial(serial_port)

    localizer_instance = ReadyToLocalize(pozyx, None, anchors, algorithm, dimension, height, remote_id)
    localizer_instance.setup()

    sensor_data = None
    if config_data.get("sensor_data"):
        sensor_data = Orientation3D(pozyx, None, remote_id)
        sensor_data.setup()

    return {"localizer": localizer_instance, "sensor_data": sensor_data}


def read_poszyx(queue_instance, data_controllers):
    while True:
        data = {"timestamp": datetime.datetime.utcnow().isoformat()}

        position = data_controllers["localizer"].loop()

        if not position:
            continue

        data.update(position)

        if data_controllers.get("sensor_data"):
            sensor_data = data_controllers["sensor_data"].loop()

            if not sensor_data:  # we don't want inconsistent data if we want acceleration data etc..
                continue

            data.update(sensor_data)

        queue_instance.put(data)


if __name__ == "__main__":
    session_data = get_config(sensor_data=True)

    session_data["location_description"] = "tuin molenbeek"
    session_data["description"] = "refactor test"


    # store the meta data
    session = store_session_meta_data(session_data)
    session_data["id"] = session.data.as_data()["attributes"]["raw-tracking-session-id"]


    # start streaming
    queue = get_queue()
    http_session = get_http_session()
    session_id = session_data["id"]

    # first queue reader
    callback_storage = lambda data: store_tracking_session_location_element(get_http_session(), session_id, data)
    start_daemon_process(queue_reader, (callback_storage, queue,))


    # setup pozyx
    localizer = setup_poszyx(session_data)

    # write
    start_daemon_process(read_poszyx, (queue, localizer, ))

    # cli
    cli(queue)

    session_data["stop_time"] = datetime.datetime.utcnow().isoformat()
    session_data["data"] = get_session_data(session_id)

    print(print_stats(session_data))




