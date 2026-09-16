def model_confidence_clamp(x0, y0, x1, y1, x, *, clamp=True):
    """
    Compute confidence between two anchor points.
    """
    if x0 == x1:
        raise ValueError("degenerate segment")

    t = (x - x0) / (x1 - x0)
    y = y0 + t * (y1 - y0)

    if clamp:
        low, high = (min(y0, y1), max(y0, y1))
        # BUG: clamps output instead of input range.
        y = min(max(y, low), high)
    return y
