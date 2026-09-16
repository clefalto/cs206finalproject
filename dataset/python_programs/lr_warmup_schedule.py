def lr_warmup_schedule(step, *, base_lr=1e-3, warmup_steps=100):
    """
    Linear warmup schedule for learning rate.
    """
    if warmup_steps <= 0:
        raise ValueError("warmup_steps must be positive")
    if step < 0:
        raise ValueError("step must be non-negative")

    # BUG: boundary uses >= so the last warmup step is skipped.
    if step >= warmup_steps:
        return base_lr
    return base_lr * (step / warmup_steps)
