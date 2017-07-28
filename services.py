import jsonapi_requests
from jsonapi_requests import JsonApiObject
import requests
from multiprocessing import Process, Queue
import uuid


# JSON API STUFF
def store_session_meta_data(data):
    raw_data_id = str(uuid.uuid4())
    api = get_json_api()
    stored_anchors = store_deployed_anchors(api, data["anchors"])
    anchor_configuration = store_anchors_configuration(api, stored_anchors, data["location_description"])
    session = create_session(api, raw_data_id, data["description"], anchor_configuration, data["start_time"])
    return session


def get_json_api():
    return jsonapi_requests.Api.config({'API_ROOT': 'http://localhost'})


def create_session(api, raw_data_id, description, anchor_configuration, start_time):
    endpoint = api.endpoint('tracking-sessions')
    data = endpoint.post(object=JsonApiObject(
        attributes={'description': description,
                    "raw-tracking-data-id": raw_data_id,
                    "start-time": start_time},
        relationships={'anchors-configuration':  {"data": anchor_configuration.data.as_data()}},
        type='tracking-sessions'))

    return data


def store_anchors_configuration(api, anchors, location_description):
    endpoint = api.endpoint("anchors-configurations")

    data = endpoint.post(object=JsonApiObject(
        attributes={'description': location_description},
        relationships={'deployed-anchors': {"data": [a.data.as_data() for a in anchors]}},
        type='anchors-configurations'))

    return data


def store_deployed_anchors(api, anchors):
    stored_anchors = []

    for anchor in anchors:
        point = store_coordinates(api, anchor["coordinates"])
        endpoint = api.endpoint("deployed-anchors")

        data = endpoint.post(object=JsonApiObject(
            attributes={'anchor-label': anchor["label"]},
            relationships={"point-coordinates": {"data": point.data.as_data()}},
            type='deployed-anchors'))

        stored_anchors.append(data)

    return stored_anchors


def store_coordinates(api, coordinates_dict):
    endpoint = api.endpoint('points-coordinates')
    data = endpoint.post(object=JsonApiObject(
        attributes=coordinates_dict,
        type='points-coordinates'))
    return data


# raw data stuff
def get_http_session():
    return requests.session()


def store_tracking_session_location_element(http_session, session_id, data):
    response = http_session.patch('http://localhost/raw-trackings-data/{}/data-points'.format(session_id), json=data)


def get_session_data(session_id):
    return requests.get('http://localhost/raw-trackings-data/{}/data-points'.format(session_id)).json()


# queue
# see also
# https://stackoverflow.com/questions/11515944/how-to-use-multiprocessing-queue-in-python
def get_queue():
    return Queue()


def queue_reader(callback, queue):
    while True:
        data = queue.get()
        if data is "EXIT":
            queue.close()
            break
        callback(data)


def start_daemon_process(target, args):
    process_instance = Process(target=target, args=args)
    process_instance.daemon = True
    process_instance.start()