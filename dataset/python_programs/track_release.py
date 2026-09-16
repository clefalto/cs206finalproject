def track_release(counters, key, *, cap=None):
    """
    Increment the release counter with an optional cap.
    """
    current = counters.get(key, 0)
    updated = current + 1

    if cap is not None:
        # BUG: cap allows one extra increment.
        if updated > cap:
            updated = cap

    counters[key] = updated
    return updated
