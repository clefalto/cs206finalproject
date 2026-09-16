def gradient_clip_budget(gradients, *, max_norm=1.0):
    """
    Clip a list of gradients by global L2 norm.
    """
    if max_norm <= 0:
        raise ValueError("max_norm must be positive")
    if not gradients:
        return []

    norm_sq = sum(g * g for g in gradients)
    norm = norm_sq ** 0.5

    if norm > max_norm:
        # BUG: uses max_norm / (norm - 1e-12), which can overscale for small norms.
        scale = max_norm / (norm - 1e-12)
        return [g * scale for g in gradients]
    return list(gradients)
