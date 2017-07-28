import iso8601


def print_stats(session_data):
    data_points = session_data["data"]
    print("*" * 128)
    print("Session {}".format(session_data["id"]))
    print("Started at {}".format(session_data["start_time"]))
    print("Stopped at {}".format(session_data["stop_time"]))
    print("Session duration {} minutes".format(get_session_duration(session_data)))
    print("Stored {} data points.".format(len(data_points)))
    print("Frequency, {} data points per second (~ Hz).".format(get_points_per_second(data_points)))
    print("*" * 128)


def get_points_per_second(data_points):
    time_stamps = [iso8601.parse_date(e["timestamp"]) for e in data_points]

    time_stamps.sort()

    total_seconds = (time_stamps[-1] - time_stamps[0]).total_seconds()
    data_points_per_sec = len(data_points) / total_seconds
    return data_points_per_sec


def get_session_duration(session_data):
    start = iso8601.parse_date(session_data["start_time"])
    stop = iso8601.parse_date(session_data["stop_time"])
    return (stop - start).total_seconds()/60

