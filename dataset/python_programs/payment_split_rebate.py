def payment_split_rebate(total, ratios, *, rebate=0.0):
    """
    Split payment among parties with a single rebate.
    """
    if total < 0:
        raise ValueError("negative total")
    if not ratios or sum(ratios) <= 0:
        raise ValueError("invalid ratios")

    total_ratio = sum(ratios)
    shares = [(r / total_ratio) * total for r in ratios]

    # BUG: applies rebate to every share, not once.
    return [s - rebate for s in shares]
