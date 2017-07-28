from utils import eprint, hex_string_to_hex
from pypozyx import POZYX_POS_ALG_UWB_ONLY, POZYX_2_5D, PozyxSerial, POZYX_3D, POZYX_POS_ALG_TRACKING
from localize import get_serial_ports, SimpleUDPClient, DeviceCoordinates, ReadyToLocalize, Coordinates
from services import queue_reader, \
    start_daemon_process, store_tracking_session_location_element, get_queue, get_http_session, get_session_data, \
    store_session_meta_data

from stats import print_stats
import datetime
import uuid


def cli(queue):
    input("Press Enter to stop...")
    queue.put("EXIT")

def setup_poszyx(data):
    #shortcut to not have to find out the port yourself
    serial_port = get_serial_ports()[1].device

    remote_id = 0x6166                 # remote device network ID
    remote = False                 # whether to use a remote device
    if not remote:
        remote_id = None

    use_processing = True             # enable to send position data through OSC
    ip = "127.0.0.1"                   # IP for the OSC UDP
    network_port = 8888                # network port for the OSC UDP
    osc_udp_client = None
    if use_processing:
        osc_udp_client = SimpleUDPClient(ip, network_port)

    anchors = []

    for anchor in data["anchors"]:
        # necessary data for calibration, change the IDs and coordinates yourself
        device_coordinates = DeviceCoordinates(hex_string_to_hex(anchor["label"]),
                                               anchor["type"],
                                               Coordinates(anchor["coordinates"]["x-value"],
                                                           anchor["coordinates"]["y-value"],
                                                           anchor["coordinates"]["z-value"]))
        anchors.append(device_coordinates)


    # algorithm = POZYX_POS_ALG_TRACKING  # positioning algorithm to use
    # dimension = POZYX_3D              # positioning dimension

    algorithm = POZYX_POS_ALG_UWB_ONLY  # positioning algorithm to use
    dimension = POZYX_2_5D
    height = 800                      # height of device, required in 2.5D positioning

    pozyx = PozyxSerial(serial_port)
    localizer = ReadyToLocalize(pozyx, osc_udp_client, anchors, algorithm, dimension, height, remote_id)
    localizer.setup()

    return localizer


def read_poszyx(queue_instance, localizer):
    while True:
        position = localizer.loop()
        data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "x-value": position.x,
            "y-value": position.y,
            "z-value": position.z
        }

        queue_instance.put(data)


if __name__ == "__main__":
    session_data = {"start_time": datetime.datetime.utcnow().isoformat(),
                    "anchors": [
                        {"label": "0x613e", "type": 1, "coordinates": {"x-value": 0, "y-value": 1270, "z-value": 2000}},
                        {"label": "0x6107", "type": 1, "coordinates": {"x-value": 1445, "y-value": 0, "z-value": 2000}},
                        {"label": "0x6136", "type": 1, "coordinates": {"x-value": 1445, "y-value": 1270, "z-value": 2000}},
                        {"label": "0x6166", "type": 1, "coordinates": {"x-value": 0, "y-value": 0, "z-value": 1000}}
                    ],
                    "location_description": "somewhere in molenbeek",
                    "description": "last time"}

    # store the meta data
    session = store_session_meta_data(session_data)
    session_data["id"] = session.data.as_data()["attributes"]["raw-tracking-data-id"]


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




