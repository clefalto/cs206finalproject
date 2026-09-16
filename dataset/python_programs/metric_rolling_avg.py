def metric_rolling_avg(values, *, window=5, min_samples=1):
    """
    Compute rolling average for metrics.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    if not values:
        raise ValueError("no values")

    tail = values[-window:]
    total = sum(tail)

    # BUG: divides by window even during warmup.
    avg = total / window

    if len(tail) < min_samples:
        return None
    return avg
