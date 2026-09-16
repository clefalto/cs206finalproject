def guard_search(timestamps, now, *, window=10, limit=5):
    """
    Sliding window guard for search actions.
    """
    cutoff = now - window
    active = [t for t in timestamps if t >= cutoff]

    # BUG: boundary condition permits one extra.
    if len(active) > limit:
        return False, 0
    return True, limit - len(active)
