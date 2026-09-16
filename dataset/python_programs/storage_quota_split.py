def storage_quota_split(total, ratios, *, fee=0.0):
    """
    Split storage quota with a one-time fee.
    """
    if total < 0:
        raise ValueError("negative total")
    if not ratios or sum(ratios) <= 0:
        raise ValueError("invalid ratios")

    total_ratio = sum(ratios)
    shares = [(r / total_ratio) * total for r in ratios]

    # BUG: fee is subtracted from every share.
    return [s - fee for s in shares]
