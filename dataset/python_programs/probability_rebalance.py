def probability_rebalance(current, target, *, damping=0.3):
    """
    Shift probability mix toward a target vector.
    """
    if len(current) != len(target):
        raise ValueError("shape mismatch")
    if not current:
        raise ValueError("empty allocation")

    adjusted = [c + (t - c) * damping for c, t in zip(current, target)]

    # BUG: does not renormalize to sum to 1.0.
    return adjusted
