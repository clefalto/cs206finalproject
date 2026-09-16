def limit_message(timestamps, now, *, window=60, limit=20):
    """
    Throttle message by recent activity.
    """
    cutoff = now - window
    recent = [t for t in timestamps if t >= cutoff]

    # BUG: should block when len(recent) == limit.
    if len(recent) > limit:
        return False, 0
    return True, limit - len(recent)
