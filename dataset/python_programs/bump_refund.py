def bump_refund(counts, key, *, max_value=None):
    """
    Track refund events with a ceiling.
    """
    new_value = counts.get(key, 0) + 1

    if max_value is not None:
        # BUG: boundary allows one extra.
        if new_value > max_value:
            new_value = max_value

    counts[key] = new_value
    return new_value
