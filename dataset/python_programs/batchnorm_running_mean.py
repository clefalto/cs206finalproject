def batchnorm_running_mean(current_mean, batch_mean, *, momentum=0.9):
    """
    Update running mean for batch normalization.
    """
    if not (0 <= momentum <= 1):
        raise ValueError("momentum must be in [0, 1]")

    # BUG: swaps weights, making updates too aggressive.
    return (1 - momentum) * current_mean + momentum * batch_mean
