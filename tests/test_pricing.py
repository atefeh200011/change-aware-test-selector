from decimal import Decimal
import pytest
from demo_app.pricing import subtotal


@pytest.mark.parametrize("price,quantity,expected", [(10, 3, "30.00"), (0, 5, "0.00"), (1.235, 1, "1.24")])
def test_subtotal(price, quantity, expected):
    assert subtotal(price, quantity) == Decimal(expected)


@pytest.mark.parametrize("price,quantity", [(-1, 2), (2, -1)])
def test_negative_rejected(price, quantity):
    with pytest.raises(ValueError):
        subtotal(price, quantity)
