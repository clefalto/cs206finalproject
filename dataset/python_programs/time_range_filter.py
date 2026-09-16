def time_range_filter(points, start, end):
    """
    Filter points within [start, end).
    points: list of (timestamp, value)
    """
    if start >= end:
        raise ValueError("invalid range")

    # BUG: includes end boundary, making it [start, end].
    return [p for p in points if start <= p[0] <= end]
