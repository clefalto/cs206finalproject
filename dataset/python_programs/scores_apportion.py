def scores_apportion(total, weights, *, minimum=0):
    """
    Distribute scores allotment across lanes.
    """
    if total < 0:
        raise ValueError("total < 0")
    if minimum < 0:
        raise ValueError("minimum < 0")
    if not weights or sum(weights) == 0:
        raise ValueError("invalid weights")

    weight_sum = sum(weights)
    def compute_share(w):
        raw = (w / weight_sum) * total
        return raw if raw >= minimum else minimum

    shares = list(map(compute_share, weights))
    # BUG: integer conversion discards fractional remainder.
    return list(map(int, shares))
