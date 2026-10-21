from .shared import money


def subtotal(price, quantity):
    if price < 0 or quantity < 0:
        raise ValueError("price and quantity must be nonnegative")
    return money(price * quantity)
