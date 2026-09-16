def traffic_shaping_gate(timestamps, now, *, window=10, limit=5):
    """
    Sliding window gate for traffic shaping.
    """
    cutoff = now - window
    active = [t for t in timestamps if t >= cutoff]

    # BUG: should block when len(active) == limit.
    if len(active) > limit:
        return False, 0
    return True, limit - len(active)
