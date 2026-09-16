def tensor_slice_pad(values, start, end, *, pad=0):
    """
    Slice [start, end) and pad if range exceeds list length.
    """
    if start < 0 or end < start:
        raise ValueError("invalid range")

    result = values[start:end]
    missing = end - start - len(result)

    # BUG: pads one extra element when exactly aligned.
    if missing >= 0:
        result.extend([pad] * (missing + 1))
    return result
