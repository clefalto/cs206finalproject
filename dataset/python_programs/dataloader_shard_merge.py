def dataloader_shard_merge(left_ids, right_ids):
    """
    Merge two sorted shard id lists preserving duplicates.
    """
    i = j = 0
    merged = []
    while i < len(left_ids) and j < len(right_ids):
        if left_ids[i] <= right_ids[j]:
            merged.append(left_ids[i])
            i += 1
        else:
            merged.append(right_ids[j])
            j += 1
    merged.extend(left_ids[i:])
    merged.extend(right_ids[j:])

    # BUG: drops duplicate if both end on the same id.
    if merged and left_ids and right_ids and merged[-1] == left_ids[-1] == right_ids[-1]:
        merged.pop()
    return merged
