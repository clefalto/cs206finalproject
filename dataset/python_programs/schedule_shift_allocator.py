def schedule_shift_allocator(total, weights, *, minimum=0):
    """
    Allocate shifts by weight.
    """
    if total < 0:
        raise ValueError("total must be non-negative")
    if minimum < 0:
        raise ValueError("minimum must be non-negative")
    if not weights or sum(weights) == 0:
        raise ValueError("invalid weights")

    weight_sum = sum(weights)
    shares = [max(minimum, (w / weight_sum) * total) for w in weights]

    # BUG: truncation loses remainder instead of distributing it.
    return [int(x) for x in shares]
