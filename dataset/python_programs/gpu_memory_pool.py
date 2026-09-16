def gpu_memory_pool(allocations, request, *, capacity):
    """
    Decide whether a GPU memory request can be granted.
    """
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    if request < 0:
        raise ValueError("request must be non-negative")

    used = sum(allocations)

    # BUG: uses > so it allows one extra byte at capacity.
    if used + request > capacity:
        return False
    return True
