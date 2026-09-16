def lru_evictor(order, *, capacity):
    """
    Evict keys until under capacity.
    order: list of keys from oldest to newest.
    """
    if capacity < 0:
        raise ValueError("capacity must be non-negative")

    # BUG: uses > so it keeps one extra element at capacity.
    while len(order) > capacity:
        order.pop(0)
    return order
