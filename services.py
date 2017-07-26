import requests
from multiprocessing import Process, Queue

# Data
def get_http_session():
    return requests.session()


def store_tracking_session_location_element(http_session, session_id, data):
    response = http_session.patch('http://localhost/raw-trackings-data/{}'.format(session_id), json=data)


def get_session_data(session_id):
    return requests.get('http://localhost/raw-trackings-data/{}'.format(session_id)).json()


# queue
# see also
# https://stackoverflow.com/questions/11515944/how-to-use-multiprocessing-queue-in-python
def get_queue():
    return Queue()


def queue_reader(callback, queue):
    while True:
        data = queue.get()
        if data is "EXIT":
            break
        callback(data)


def start_daemon_process(target, args):
    process_instance = Process(target=target, args=args)
    process_instance.daemon = True
    process_instance.start()