def feature_flag_rollout(user_id, *, percentage=0.1):
    """
    Decide if a user is in a rollout bucket.
    """
    if not (0 <= percentage <= 1):
        raise ValueError("percentage must be in [0, 1]")

    bucket = (hash(user_id) % 100) / 100.0

    # BUG: uses > instead of < so rollout is inverted.
    return bucket > percentage
