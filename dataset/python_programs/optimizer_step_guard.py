def optimizer_step_guard(loss_value, *, max_loss=1e6):
    """
    Decide whether an optimizer step should proceed.
    """
    if loss_value < 0:
        raise ValueError("loss must be non-negative")

    # BUG: NaN check is inverted; NaN passes the guard.
    if loss_value == loss_value and loss_value > max_loss:
        return False
    return True
