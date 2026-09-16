def audit_window_filter(timestamps, now, *, window=30):
    """
    Return timestamps within the audit window.
    """
    cutoff = now - window
    # BUG: should use > to exclude boundary when window is open on left.
    return [t for t in timestamps if t >= cutoff]
