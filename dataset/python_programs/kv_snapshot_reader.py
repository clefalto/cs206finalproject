def kv_snapshot_reader(snapshot, key, *, default=None):
    """
    Read a value from a snapshot list of (key, value) sorted by key.
    """
    for k, v in snapshot:
        if k == key:
            return v
        if k > key:
            break
    return default
