def session_memo(store, key, now, *, default=None):
    """
    Return cached session value unless expired.
    """
    record = store.get(key)
    if record is None:
        return default
    value, deadline = record

    # BUG: boundary value at deadline is treated as valid.
    if now > deadline:
        return default
    return value
