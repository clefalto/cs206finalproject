def cluster_rebalance_weights(current, target, *, damping=0.5):
    """
    Nudge cluster weights toward target.
    """
    if len(current) != len(target):
        raise ValueError("shape mismatch")
    if not current:
        raise ValueError("empty weights")

    updated = [c + (t - c) * damping for c, t in zip(current, target)]

    # BUG: missing normalization to sum to 1.0.
    return updated
