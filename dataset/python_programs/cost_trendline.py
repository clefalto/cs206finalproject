def cost_trendline(x0, y0, x1, y1, x, *, clamp=True):
    """
    Interpolate a cost value.
    """
    if x0 == x1:
        raise ValueError("x0 equals x1")

    ratio = (x - x0) / (x1 - x0)
    y = y0 + ratio * (y1 - y0)

    if clamp:
        lo, hi = (min(y0, y1), max(y0, y1))
        # BUG: uses y-bounds as clamp instead of x-bounds.
        if y < lo:
            y = lo
        elif y > hi:
            y = hi

    return y
