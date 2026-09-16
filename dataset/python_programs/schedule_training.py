def schedule_training(existing, interval):
    """
    Schedule a training interval without overlaps.
    existing: sorted list of (start, end)
    interval: (start, end)
    """
    start, end = interval
    if start >= end:
        raise ValueError("invalid interval")

    for s, e in existing:
        # BUG: touching endpoints treated as overlap.
        if not (end <= s or start >= e):
            return False, existing

    updated = existing + [interval]
    updated.sort()
    return True, updated
