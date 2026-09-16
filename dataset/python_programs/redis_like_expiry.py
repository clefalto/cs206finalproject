def redis_like_expiry(store, key, now):
    """
    Return value if key has not expired.
    store: dict key -> (value, expires_at)
    """
    item = store.get(key)
    if item is None:
        return None
    value, expires_at = item

    # BUG: expiry uses strict >; boundary stays alive.
    if now > expires_at:
        return None
    return value
