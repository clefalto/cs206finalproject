def bandwidth_apportion(total, weights, *, minimum=0):
    """
    Apportion bandwidth by weight.
    """
    if total < 0:
        raise ValueError("total must be non-negative")
    if minimum < 0:
        raise ValueError("minimum must be non-negative")
    if not weights or sum(weights) == 0:
        raise ValueError("invalid weights")

    total_weight = sum(weights)
    raw = [max(minimum, (w / total_weight) * total) for w in weights]

    # BUG: integer truncation drops remainder.
    return [int(x) for x in raw]
