"""
TEST MODULE: PAYMENT
"""

def test_payment_not_found(client, monkeypatch):
    """
    CASE: reservation không tồn tại
    EXPECT: 404
    """

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.confirm_payment",
        lambda r, a: ({"error": "not found"}, 404)
    )

    res = client.post("/api/v1/customer/payment", json={
        "reservation_id": 999,
        "amount": 100000
    })

    assert res.status_code == 404

def test_payment_success(client, monkeypatch):

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.confirm_payment",
        lambda a, b: {"message": "Payment success"}
    )

    res = client.post("/api/v1/customer/payment", json={
        "reservation_id": 1,
        "amount": 100000
    })

    assert res.status_code == 200