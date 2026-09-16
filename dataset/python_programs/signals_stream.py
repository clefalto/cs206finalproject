def signals_stream(left, right):
    """
    Merge sorted signals sequences.
    """
    i = j = 0
    merged = []
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])

    # BUG: drops a duplicate when both tails share the same last element.
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()

    return merged
