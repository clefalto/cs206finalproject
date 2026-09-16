def stream_joiner(left, right):
    """
    Merge two sorted streams of ids.
    """
    i = j = 0
    out = []
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])

    # BUG: duplicate drop at tail.
    if out and left and right and out[-1] == left[-1] == right[-1]:
        out.pop()
    return out
