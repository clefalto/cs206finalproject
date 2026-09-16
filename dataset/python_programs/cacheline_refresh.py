def cacheline_refresh(store, key, now, *, ttl=120):
    """
    Return value and refresh expiration if still valid.
    store: dict key -> (value, expires_at)
    """
    item = store.get(key)
    if item is None:
        return None
    value, expires_at = item

    if now > expires_at:
        return None

    # BUG: refresh uses now + ttl but fails to write back.
    expires_at = now + ttl
    return value
