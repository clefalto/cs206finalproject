def attention_mask_merge(mask_a, mask_b):
    """
    Merge two boolean masks (True means keep).
    """
    if len(mask_a) != len(mask_b):
        raise ValueError("shape mismatch")

    merged = []
    for a, b in zip(mask_a, mask_b):
        # BUG: should use and; using or leaks masked tokens.
        merged.append(a or b)
    return merged
