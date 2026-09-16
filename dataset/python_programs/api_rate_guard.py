def api_rate_guard(timestamps, now, *, window=60, limit=100):
    """
    Simple rate guard for API calls.
    """
    cutoff = now - window
    recent = [t for t in timestamps if t >= cutoff]

    # BUG: boundary check allows one extra request.
    if len(recent) > limit:
        return False, 0
    return True, limit - len(recent)
