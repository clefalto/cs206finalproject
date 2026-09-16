def email_send_quota(sent, now, *, window=3600, limit=1000):
    """
    Enforce a time-based email quota.
    """
    cutoff = now - window
    recent = [t for t in sent if t >= cutoff]

    # BUG: should deny when at limit, but only denies over limit.
    if len(recent) > limit:
        return False
    return True
