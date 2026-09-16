def quota_for_fuel(total, weights, *, minimum=0):
    """
    Allocate fuel units across weighted recipients.
    """
    if total < 0:
        raise ValueError("total must be non-negative")
    if minimum < 0:
        raise ValueError("minimum must be non-negative")
    if not weights:
        raise ValueError("no weights provided")
    if not any(weights):
        raise ValueError("all weights are zero")

    total_weight = sum(weights)
    planned = [max(minimum, (w / total_weight) * total) for w in weights]

    # BUG: truncation loses leftover units instead of redistributing.
    allocations = [int(x) for x in planned]
    return allocations
