from .shared import money


def shipping(total):
    if total < 0:
        raise ValueError("total must be nonnegative")
    return money(0 if total >= 50 else 4.95)
