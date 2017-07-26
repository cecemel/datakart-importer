from utils import eprint
from pypozyx import POZYX_POS_ALG_UWB_ONLY, POZYX_2_5D, PozyxSerial, POZYX_3D, POZYX_POS_ALG_TRACKING
from localize import get_serial_ports, SimpleUDPClient, DeviceCoordinates, ReadyToLocalize, Coordinates
from services import queue_reader, \
    start_daemon_process, store_tracking_session_location_element, get_queue, get_http_session, get_session_data

from stats import get_points_per_second
import datetime


def cli(queue):
    input("Press Enter to stop...")
    queue.put("EXIT")


def read_poszyx(queue):
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
    # necessary data for calibration, change the IDs and coordinates yourself
    anchors = [DeviceCoordinates(0x6107, 1, Coordinates(1445, 0, 2000)),
               DeviceCoordinates(0x613e, 1, Coordinates(0, 1270, 2000)),
               DeviceCoordinates(0x6166, 1, Coordinates(0, 0, 1000)),
               DeviceCoordinates(0x6136, 1, Coordinates(1445, 1270, 2000))]

    #algorithm = POZYX_POS_ALG_TRACKING  # positioning algorithm to use
    #dimension = POZYX_3D              # positioning dimension

    algorithm = POZYX_POS_ALG_UWB_ONLY  # positioning algorithm to use
    dimension = POZYX_2_5D
    height = 800                      # height of device, required in 2.5D positioning

    pozyx = PozyxSerial(serial_port)
    r = ReadyToLocalize(pozyx, osc_udp_client, anchors, algorithm, dimension, height, remote_id)
    r.setup()

    while True:
        position = r.loop()
        data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "x-value": position.x,
            "y-value": position.y,
            "z-value": position.z
        }

        queue.put(data)

if __name__ == "__main__":
    queue = get_queue()
    http_session = get_http_session()
    session_id = "test61"

    # first queue reader
    callback_storage = lambda data: store_tracking_session_location_element(get_http_session(), session_id, data)
    start_daemon_process(queue_reader, (callback_storage, queue,))


    # write
    start_daemon_process(read_poszyx, (queue,))

    # cli
    cli(queue)

    data = get_session_data(session_id)
    print(get_points_per_second(data))




