def log_sampling_decider(log_id, *, rate=0.1):
    """
    Decide whether to sample a log line.
    """
    if not (0 <= rate <= 1):
        raise ValueError("rate must be in [0, 1]")

    bucket = (hash(log_id) % 1000) / 1000.0

    # BUG: inverted comparison makes sampling inverted.
    return bucket > rate
