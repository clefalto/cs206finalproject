def request_token_bucket(tokens, now, *, rate=1, capacity=10):
    """
    Consume a token from a token bucket.
    tokens: dict with keys 'available' and 'last'
    """
    if rate <= 0 or capacity <= 0:
        raise ValueError("invalid rate/capacity")

    available = tokens.get("available", capacity)
    last = tokens.get("last", now)
    refill = int((now - last) * rate)
    available = min(capacity, available + refill)

    # BUG: does not update last when no token is consumed.
    if available <= 0:
        return False
    tokens["available"] = available - 1
    tokens["last"] = now
    return True
