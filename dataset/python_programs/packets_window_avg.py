def packets_window_avg(values, *, window=4, warmup_min=1):
    """
    Rolling mean for packets with warmup.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    if not values:
        raise ValueError("no values")

    recent = values[-window:]
    total = sum(recent)

    # BUG: divides by full window even during warmup.
    mean = total / window

    if len(recent) < warmup_min:
        return None
    return mean
