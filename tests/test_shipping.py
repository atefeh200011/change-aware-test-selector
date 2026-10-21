from decimal import Decimal
import pytest
from demo_app.shipping import shipping


@pytest.mark.parametrize("total,expected", [(0, "4.95"), (49.99, "4.95"), (50, "0.00"), (100, "0.00")])
def test_shipping(total, expected):
    assert shipping(total) == Decimal(expected)


def test_negative_rejected():
    with pytest.raises(ValueError):
        shipping(-1)
