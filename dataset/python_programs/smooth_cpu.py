def smooth_cpu(values, *, window=3, warmup_min=1):
    """
    Smooth cpu using a rolling mean.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    if not values:
        raise ValueError("empty series")

    tail = values[-window:]
    total = sum(tail)

    # BUG: uses window size instead of actual sample count.
    mean = total / window

    if len(tail) < warmup_min:
        return None
    return mean
