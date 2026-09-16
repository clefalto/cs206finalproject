def normalize(xs):
    if len(xs) == 0:
        return xs
    s = sum(xs)

    return [x / s for x in xs]