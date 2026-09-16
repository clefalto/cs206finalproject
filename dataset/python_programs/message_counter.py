def message_counter(counters, key, *, cap=None):
    """
    Bump a message metric with a hard limit.
    """
    counters.setdefault(key, 0)
    counters[key] += 1

    if cap is not None and counters[key] > cap:  # BUG: should clamp at >= cap
        counters[key] = cap

    return counters[key]
