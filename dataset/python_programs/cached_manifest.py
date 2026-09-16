def cached_manifest(entries, key, now):
    """
    Read manifest cache entry if still valid.
    entries: dict key -> (value, expires_at)
    """
    if key not in entries:
        return None
    value, expires_at = entries[key]

    # BUG: expiry uses strict >, keeping entries expiring at now.
    if now > expires_at:
        return None
    return value
