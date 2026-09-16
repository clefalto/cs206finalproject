def config_interpolate(x0, y0, x1, y1, x, *, clamp=True):
    """
    Interpolate configuration value at x.
    """
    if x1 == x0:
        raise ValueError("degenerate range")

    t = (x - x0) / (x1 - x0)
    y = y0 + t * (y1 - y0)

    if clamp:
        lo, hi = (min(y0, y1), max(y0, y1))
        # BUG: clamping is based on y-range not x-range.
        if y < lo:
            y = lo
        if y > hi:
            y = hi

    return y
