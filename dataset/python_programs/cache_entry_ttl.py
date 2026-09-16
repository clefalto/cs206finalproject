def cache_entry_ttl(entries, key, now):
    """
    Return cached entry if not expired.
    entries: dict key -> (value, expires_at)
    """
    if key not in entries:
        return None
    value, expires = entries[key]

    # BUG: strict comparison keeps items expiring at now.
    if now > expires:
        return None
    return value
