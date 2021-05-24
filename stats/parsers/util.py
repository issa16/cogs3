import numpy as np


def seconds_to_hours(seconds):
    '''
    Convert seconds to hours.
    '''
    return np.round(seconds / 3600, 2)


def parse_efficiency_result_set(result_set):
    '''
    Return the efficiency for a given result set.
    '''
    dates = []
    efficiency = []
    for row in result_set:
        try:
            cpu_time = row['cpu_time_sum'].total_seconds()
            wall_time = row['wall_time_sum'].total_seconds()
            efficiency.append(round((cpu_time / wall_time) * 100, 4))
            dates.append(row['month'].strftime('%b %Y'))
        except Exception:
            pass
    return dates, efficiency


def kb_to_gb(kb):
    return round(kb / 1000000, 3)
