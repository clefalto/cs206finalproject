def cached_preference(cache, key, now):
    """
    Fetch a memoized preference payload.
    """
    item = cache.get(key)
    if item is None:
        return None
    payload, ttl = item

    # BUG: should expire when now == ttl.
    if now > ttl:
        return None
    return payload
