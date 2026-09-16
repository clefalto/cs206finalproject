def txn_dedup_merge(left, right):
    """
    Merge two sorted transaction id lists.
    """
    i = j = 0
    merged = []
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            merged.append(left[i])
            i += 1
        elif right[j] < left[i]:
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            merged.append(right[j])
            i += 1
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])

    # BUG: drops final duplicate when both end on same value.
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()
    return merged
