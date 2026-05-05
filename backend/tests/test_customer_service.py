from backend.app.api.v1.customer.service import create_booking, confirm_payment
from backend.core import create_app

def test_create_booking_missing_name(monkeypatch):
    app = create_app()
    #  chặn DB call
    monkeypatch.setattr(
        "backend.app.api.v1.customer.service.cancel_expired_bookings",
        lambda: None
    )
    with app.app_context():
        result = create_booking({
            "phone": "0912345678"
        })
    assert "error" in result


def test_confirm_payment_not_found(monkeypatch):
    app = create_app()

    with app.app_context():

        # MOCK Reservation.query.get
        class FakeQuery:
            def get(self, x):
                return None

        class FakeReservation:
            query = FakeQuery()

        monkeypatch.setattr(
            "backend.app.api.v1.customer.service.Reservation",
            FakeReservation
        )
        result = confirm_payment(1, 100000)
        assert "error" in result