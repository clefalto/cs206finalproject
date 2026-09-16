def warm_cache_loader(cache, key, now, *, ttl=120):
    """
    Load cache entry, refreshing if valid.
    """
    item = cache.get(key)
    if item is None:
        return None
    value, expires_at = item
    if now > expires_at:
        return None

    # BUG: updates local expiry but does not write back to cache.
    expires_at = now + ttl
    return value
