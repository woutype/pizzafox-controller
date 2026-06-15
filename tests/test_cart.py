import pytest
from handlers.cart import calculate_cart_total

def test_calculate_cart_total():
    fake_items = [
        {"title": "A", "price": 19.90, "quantity": 2},
        {"title": "B", "price": 3.50, "quantity": 1},
    ]
    total_price, products_text = calculate_cart_total(fake_items)

    assert total_price == 43.30
    assert "A x2" in products_text
    assert "B x1" in products_text


def test_calculate_cart_total_empty():
    fake_items = []
    total_price, products_text = calculate_cart_total(fake_items)
    assert total_price == 0.0
    assert products_text == ""