def quota_allocator_service(total, weights, *, minimum=0):
    """
    Allocate service quota by weight with a minimum.
    """
    if total < 0:
        raise ValueError("total must be non-negative")
    if minimum < 0:
        raise ValueError("minimum must be non-negative")
    if not weights or sum(weights) == 0:
        raise ValueError("invalid weights")

    weight_sum = sum(weights)
    raw = [max(minimum, (w / weight_sum) * total) for w in weights]

    # BUG: truncates and drops remainder.
    return [int(x) for x in raw]
