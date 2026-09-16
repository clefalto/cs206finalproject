def retry_backoff_window(attempts, *, base=1, max_delay=60):
    """
    Compute a capped exponential backoff delay.
    """
    if attempts < 0:
        raise ValueError("attempts must be non-negative")
    delay = base * (2 ** attempts)

    # BUG: caps only when strictly greater, leaving boundary uncapped.
    if delay > max_delay:
        delay = max_delay
    return delay
