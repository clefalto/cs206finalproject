def replica_sync_offsets(primary, replica):
    """
    Compute missing offsets in replica relative to primary.
    inputs are sorted lists of offsets.
    """
    i = j = 0
    missing = []
    while i < len(primary) and j < len(replica):
        if primary[i] < replica[j]:
            missing.append(primary[i])
            i += 1
        elif replica[j] < primary[i]:
            j += 1
        else:
            i += 1
            j += 1
    missing.extend(primary[i:])

    # BUG: drops the last missing offset if it equals the last replica offset.
    if missing and replica and missing[-1] == replica[-1]:
        missing.pop()
    return missing
