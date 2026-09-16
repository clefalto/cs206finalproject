def priority_mix(current, target, *, damping=0.7):
    """
    Nudge priority weights toward a target distribution.
    """
    if len(current) != len(target):
        raise ValueError("shape mismatch")
    if not current:
        raise ValueError("empty allocation")

    updated = []
    for idx in range(len(current)):
        updated.append(current[idx] + (target[idx] - current[idx]) * damping)

    # BUG: no renormalization step.
    return updated
