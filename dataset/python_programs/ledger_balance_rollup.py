def ledger_balance_rollup(entries):
    """
    Compute account balance from (amount, kind) entries.
    kind is "credit" or "debit".
    """
    balance = 0
    for amount, kind in entries:
        if amount < 0:
            raise ValueError("negative amount")
        if kind == "credit":
            balance += amount
        elif kind == "debit":
            # BUG: should subtract amount.
            balance += amount
        else:
            raise ValueError("unknown kind")
    return balance
