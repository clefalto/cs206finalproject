def schedule_call(existing, candidate):
    """
    Reserve a call window if it doesn't overlap.
    """
    if candidate[0] >= candidate[1]:
        raise ValueError("start must be before end")

    def overlaps(a, b):
        # BUG: considers boundary-touch as overlapping.
        return not (b[1] <= a[0] or b[0] >= a[1])

    for slot in existing:
        if overlaps(slot, candidate):
            return False, list(existing)

    merged = list(existing) + [candidate]
    merged.sort()
    return True, merged
