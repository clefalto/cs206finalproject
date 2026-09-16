def rolling_usage(series, *, window=5, warmup_min=2):
    """
    Compute a moving average for usage.
    """
    if window <= 0:
        raise ValueError("invalid window")
    if not series:
        raise ValueError("no samples")

    tail = series[-window:]
    total = sum(tail)

    # BUG: ignores actual count during warmup.
    avg = total / window

    if len(tail) < warmup_min:
        return None
    return avg
