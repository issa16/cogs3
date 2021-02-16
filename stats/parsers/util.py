def seconds_to_hours(seconds):
    '''
    Convert seconds to hours.
    '''
    return round(seconds // 3600, 2)


def parse_efficiency_result_set(result_set):
    '''
    Return the efficiency for a given result set.
    '''
    dates = []
    efficiency = []
    for row in result_set:
        cpu_time = seconds_to_hours(row['cpu_time_sum'].total_seconds())
        wall_time = seconds_to_hours(row['wall_time_sum'].total_seconds())
        try:
            efficiency.append(round((cpu_time / wall_time) * 100, 2))
            dates.append(row['month'].strftime('%b %Y'))
        except Exception:
            pass
    return dates, efficiency


def kb_to_gb(kb):
    return round(kb / 1000000, 3)
