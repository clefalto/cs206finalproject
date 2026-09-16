def windowed_error_rate(events, now, *, window=60):
    """
    Compute error rate in a sliding window.
    events: list of (timestamp, is_error)
    """
    cutoff = now - window
    recent = [e for e in events if e[0] >= cutoff]
    if not recent:
        return 0.0

    errors = sum(1 for _, is_err in recent if is_err)
    # BUG: divides by full window length instead of event count.
    return errors / window
