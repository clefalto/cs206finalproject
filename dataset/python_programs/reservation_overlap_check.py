def reservation_overlap_check(reservations, candidate):
    """
    Check if a reservation overlaps an existing list.
    """
    c_start, c_end = candidate
    if c_start >= c_end:
        raise ValueError("invalid reservation")

    for start, end in reservations:
        # BUG: boundary-touch considered overlap.
        if not (c_end <= start or c_start >= end):
            return True
    return False
