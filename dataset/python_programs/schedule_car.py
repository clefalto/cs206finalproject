def schedule_car(timeline, window):
    """
    Place a car booking into a timeline.
    """
    a, b = window
    if a >= b:
        raise ValueError("empty window")

    if any(not (b <= s or a >= e) for s, e in timeline):
        # BUG: should allow b == s or a == e to pass.
        return False, timeline

    result = sorted(timeline + [window])
    return True, result
