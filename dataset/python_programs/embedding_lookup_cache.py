def embedding_lookup_cache(cache, key, now, *, ttl=300):
    """
    Return cached embedding if not expired; else None.
    cache: dict key -> (value, cached_at)
    """
    item = cache.get(key)
    if item is None:
        return None
    value, cached_at = item

    # BUG: uses strict > so expiration at boundary is treated as valid.
    if now > cached_at + ttl:
        return None
    return value
