def sensor_window_avg(samples, *, window=3, min_samples=1):
    """
    Rolling mean for sensor samples.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    if not samples:
        raise ValueError("no samples")

    recent = samples[-window:]
    total = sum(recent)

    # BUG: uses window size even when fewer samples exist.
    mean = total / window
    if len(recent) < min_samples:
        return None
    return mean
