import json
from os import listdir
from os.path import isfile, join
from services import get_http_session

def import_data():
    session_id = "586d4f70-61d0-4631-ad98-70480e1a1876"
    path = "raw-json-files"
    files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]

    i = 0
    http_session = get_http_session()
    all_data = []
    for _file in files:
        i += 1
        with open(_file, 'r') as _file_instance:
            json_data = json.loads(_file_instance.read())

            if type(json_data) is not dict:
                print("is not dict")
                continue
            response = http_session.post('http://localhost/raw-tracking-sessions/{}/data-points'.format(session_id),
                                         json=json_data)

            if response.status_code >= 300:
                print(json_data)
                raise "hello"

            all_data.append(json_data)



            print("importing....{}".format(str(i)))


    # response = http_session.post('http://localhost/raw-tracking-sessions/{}/data-points'.format(session_id),
    #                              json=all_data[0])
    #
    # print(response.status_code)

    # grouped_data = [all_data[0: 1000], all_data[1001: 2000], all_data[2001:3000],
    #                 all_data[3001: 4000], all_data[4001:5000], all_data[5001:6000], all_data[6001:6116]]
    #
    # for g_d in grouped_data:
    #     response = http_session.post('http://localhost/raw-tracking-sessions/{}/data-points'.format(session_id),
    #                                  json=g_d)
    #     print("ok")


if __name__ == "__main__":
    import_data()