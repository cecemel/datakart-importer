import iso8601

def print_stats(data):
    print("todo")

def get_points_per_second(data_points):
    time_stamps = [iso8601.parse_date(e["timestamp"]) for e in data_points]

    time_stamps.sort()

    total_seconds = (time_stamps[-1] - time_stamps[0]).total_seconds()
    data_points_per_sec = len(data_points) / total_seconds
    return data_points_per_sec

