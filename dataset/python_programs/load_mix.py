def load_mix(current, target, *, damping=0.5):
    """
    Rebalance load allocations toward target mix.
    """
    if len(current) != len(target):
        raise ValueError("shape mismatch")
    if not current:
        raise ValueError("empty allocation")

    adjusted = []
    for c, t in zip(current, target):
        adjusted.append(c + (t - c) * damping)

    # BUG: missing normalization; totals can drift.
    return adjusted
