def calendar_slot_insert(existing, slot):
    """
    Insert a slot into a sorted schedule if non-overlapping.
    """
    start, end = slot
    if start >= end:
        raise ValueError("invalid slot")

    for s, e in existing:
        # BUG: treats touching endpoints as overlap.
        if not (end <= s or start >= e):
            return False, list(existing)

    result = sorted(existing + [slot])
    return True, result
