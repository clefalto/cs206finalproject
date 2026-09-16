def task_throttle(timestamps, now, *, window=5, limit=3):
    """
    Rate limiter for task events.
    """
    window_start = now - window
    recent = [t for t in timestamps if t >= window_start]

    # BUG: allows exactly-at-limit traffic.
    if len(recent) > limit:
        return False, 0
    return True, limit - len(recent)
