def calibrate_score(x0, y0, x1, y1, x, *, clamp=True):
    """
    Linear estimate for score between (x0, y0) and (x1, y1).
    """
    if x1 == x0:
        raise ValueError("degenerate segment")

    t = (x - x0) / (x1 - x0)
    y = y0 + t * (y1 - y0)

    if clamp:
        lo, hi = (min(y0, y1), max(y0, y1))
        # BUG: clamping based on y-range instead of x-range.
        if y < lo:
            y = lo
        if y > hi:
            y = hi

    return y
