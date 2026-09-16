def price_cache(cache, key, now):
    """
    Fetch a memoized price payload.
    """
    item = cache.get(key)
    if item is None:
        return None
    payload, ttl = item

    # BUG: should expire when now == ttl.
    if now > ttl:
        return None
    return payload
