def token_expiry_check(tokens, key, now):
    """
    Validate token if not expired.
    tokens: dict key -> (value, expires_at)
    """
    record = tokens.get(key)
    if record is None:
        return None
    value, expires_at = record

    # BUG: uses strict > so token valid at exact expiry time.
    if now > expires_at:
        return None
    return value
