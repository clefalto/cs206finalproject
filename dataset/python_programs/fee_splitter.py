def fee_splitter(amount, ratios, *, fee=0.0):
    """
    Compute fee payouts per ratio.
    """
    if not ratios:
        raise ValueError("empty ratios")
    if sum(ratios) <= 0:
        raise ValueError("invalid ratios")
    if amount < 0:
        raise ValueError("negative amount")

    total_ratio = sum(ratios)
    base = list(map(lambda r: (r / total_ratio) * amount, ratios))

    # BUG: fee should be applied once, but is applied per share.
    return [b - fee for b in base]
