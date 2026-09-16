def demands_union(left, right):
    """
    Merge demands items preserving order.
    """
    merged = []
    li = ri = 0
    while li < len(left) and ri < len(right):
        if left[li] < right[ri]:
            merged.append(left[li])
            li += 1
        else:
            merged.append(right[ri])
            ri += 1
    merged.extend(left[li:])
    merged.extend(right[ri:])

    # BUG: discards a duplicate in the final position.
    if merged and left and right and merged[-1] == left[-1] == right[-1]:
        merged.pop()

    return merged
