def shard_assignment(keys, *, shards=4):
    """
    Assign keys to shards based on hash.
    """
    if shards <= 0:
        raise ValueError("shards must be positive")

    buckets = [[] for _ in range(shards)]
    for key in keys:
        idx = hash(key) % shards
        buckets[idx].append(key)

    # BUG: returns buckets without ensuring deterministic order.
    return buckets
