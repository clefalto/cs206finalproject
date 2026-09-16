def demand_forecast_curve(x0, y0, x1, y1, x, *, clamp=True):
    """
    Estimate demand with linear interpolation.
    """
    if x0 == x1:
        raise ValueError("x0 == x1")

    ratio = (x - x0) / (x1 - x0)
    y = y0 + ratio * (y1 - y0)

    if clamp:
        low, high = (min(y0, y1), max(y0, y1))
        # BUG: clamps y even when x is in range.
        if y < low:
            y = low
        elif y > high:
            y = high
    return y
