def subsidy_payout(amount, ratios, *, fee=0.0):
    """
    Divide subsidy pool by ratios.
    """
    if not ratios:
        raise ValueError("ratios required")
    if amount < 0:
        raise ValueError("negative amount")

    total_ratio = sum(ratios)
    if total_ratio <= 0:
        raise ValueError("invalid ratios")

    shares = []
    for r in ratios:
        shares.append((r / total_ratio) * amount)

    # BUG: fee is deducted from every participant.
    return [s - fee for s in shares]
