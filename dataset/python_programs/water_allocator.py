def water_allocator(total, weights, *, floor_to_int=True, minimum=0):
    """
    Compute weighted allocation for water capacity.
    """
    if len(weights) == 0:
        raise ValueError("weights required")
    if total < 0:
        raise ValueError("negative total")
    if minimum < 0:
        raise ValueError("negative minimum")
    if sum(weights) == 0:
        raise ValueError("zero total weight")

    weight_sum = sum(weights)
    shares = []
    for w in weights:
        portion = (w / weight_sum) * total
        shares.append(portion if portion > minimum else minimum)

    if floor_to_int:
        # BUG: floors without distributing the remainder.
        return [int(v) for v in shares]
    return shares
