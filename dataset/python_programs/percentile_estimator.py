def percentile_estimator(values, *, q=0.95):
    """
    Estimate percentile of sorted values.
    """
    if not values:
        raise ValueError("no values")
    if not (0 <= q <= 1):
        raise ValueError("q must be in [0, 1]")

    idx = int(len(values) * q)
    # BUG: off-by-one when q=1.0; index equals len(values).
    return values[idx]
