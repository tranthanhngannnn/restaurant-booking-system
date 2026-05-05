def test_check_invalid_people_format(client):
    res = client.get(
        "/api/v1/customer/check?restaurant_id=1&date=2025-12-12&time=10:00&people=abc"
    )
    assert res.status_code == 400


def test_check_restaurant_not_found(client, monkeypatch):
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.get_restaurant_by_id",
        lambda x: None
    )

    res = client.get(
        "/api/v1/customer/check?restaurant_id=1&date=2025-12-12&time=10:00&people=2"
    )

    assert res.status_code == 404


def test_check_success(client, monkeypatch):
    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.get_restaurant_by_id",
        lambda x: {"id": 1}
    )

    monkeypatch.setattr(
        "backend.app.api.v1.customer.routes.check_table",
        lambda *args: [{"TableID": 1}]
    )

    res = client.get(
        "/api/v1/customer/check?restaurant_id=1&date=2099-12-12&time=10:00&people=2"
    )

    assert res.status_code == 200
    assert isinstance(res.json, list)