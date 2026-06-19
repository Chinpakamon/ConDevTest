import asyncio
import datetime

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.booking import consts, repository


def run(coro):
    return asyncio.run(coro)


def _create_booking(client: TestClient, *, name: str = "Alice") -> dict:
    payload = {
        "name": name,
        "datetime": (
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
        ).isoformat(),
        "service_type": "consultation",
    }
    response = client.post("/bookings", json=payload)
    assert response.status_code == 200
    return response.json()


def test_create_booking_returns_pending_and_enqueues_worker(
    client: TestClient, enqueue_mock, future_datetime: str
):
    response = client.post(
        "/bookings",
        json={
            "name": "Alice",
            "datetime": future_datetime,
            "service_type": "haircut",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alice"
    assert body["status"] == "pending"
    enqueue_mock.assert_called_once_with(body["id"])


def test_create_booking_rejects_past_datetime(client: TestClient):
    response = client.post(
        "/bookings",
        json={
            "name": "Alice",
            "datetime": (
                datetime.datetime.now(datetime.UTC)
                - datetime.timedelta(days=1)
            ).isoformat(),
            "service_type": "haircut",
        },
    )

    assert response.status_code == 422


def test_get_booking_returns_404_for_unknown_id(client: TestClient):
    response = client.get("/bookings/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


def test_list_bookings_supports_status_filter_and_pagination(
    client: TestClient, db_session: AsyncSession
):
    first = _create_booking(client, name="Pending")
    second = _create_booking(client, name="Confirmed")

    async def mark_confirmed():
        booking = await repository.BookingRepository.select_booking_by_id(
            second["id"], db_session
        )
        await repository.BookingRepository.update_booking_status(
            booking, db_session, consts.BookingStatus.CONFIRMED
        )

    run(mark_confirmed())

    response = client.get(
        "/bookings",
        params={"status": "confirmed", "limit": 10, "offset": 0}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == second["id"]
    assert body["items"][0]["status"] == "confirmed"
    assert body["items"][0]["id"] != first["id"]


def test_delete_pending_booking_marks_it_cancelled(client: TestClient):
    booking = _create_booking(client)

    response = client.delete(f"/bookings/{booking['id']}")

    assert response.status_code == 200
    assert response.json() == {"success": True}
    get_response = client.get(f"/bookings/{booking['id']}")
    assert get_response.json()["status"] == "cancelled"


def test_delete_confirmed_booking_returns_conflict(
    client: TestClient, db_session: AsyncSession
):
    booking_data = _create_booking(client)

    async def mark_confirmed():
        booking = await repository.BookingRepository.select_booking_by_id(
            booking_data["id"], db_session
        )
        await repository.BookingRepository.update_booking_status(
            booking, db_session, consts.BookingStatus.CONFIRMED
        )

    run(mark_confirmed())

    response = client.delete(f"/bookings/{booking_data['id']}")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Only pending bookings can be cancelled"
    }
