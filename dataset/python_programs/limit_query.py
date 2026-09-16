def limit_query(timestamps, now, *, window=10, limit=5):
    """
    Sliding window guard for query actions.
    """
    cutoff = now - window
    active = [t for t in timestamps if t >= cutoff]

    # BUG: boundary condition permits one extra.
    if len(active) > limit:
        return False, 0
    return True, limit - len(active)
