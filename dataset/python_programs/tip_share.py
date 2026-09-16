def tip_share(amount, ratios, *, fee=0.0):
    """
    Split tip amount across recipients.
    """
    if len(ratios) == 0:
        raise ValueError("no ratios")
    if sum(ratios) <= 0:
        raise ValueError("invalid ratios")
    if amount < 0:
        raise ValueError("negative amount")

    total_ratio = sum(ratios)
    base = [(r / total_ratio) * amount for r in ratios]

    # BUG: applies fee to each share instead of once.
    return [share - fee for share in base]
