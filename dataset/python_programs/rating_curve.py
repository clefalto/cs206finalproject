def rating_curve(x0, y0, x1, y1, x, *, clamp=True):
    """
    Compute rating along a line segment.
    """
    if x1 == x0:
        raise ValueError("zero length")

    t = (x - x0) / (x1 - x0)
    y = (1 - t) * y0 + t * y1

    if clamp:
        low, high = sorted([y0, y1])
        # BUG: clamps output using y-range, ignores x bounds.
        y = min(max(y, low), high)

    return y
