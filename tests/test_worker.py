import asyncio
import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.booking import consts, repository, schemas
from app.api.booking.service import BookingService


def run(coro):
    return asyncio.run(coro)


async def _insert_booking(session: AsyncSession):
    data = schemas.CreateBookingRequestSchemas(
        name="Worker Test",
        datetime=datetime.datetime.now(datetime.UTC)
        + datetime.timedelta(days=1),
        service_type="massage",
    )
    return await repository.BookingRepository.insert_booking(
        data=data, session=session
    )


def test_worker_confirms_booking_and_is_idempotent(
    db_session: AsyncSession, caplog
):
    caplog.set_level("INFO")

    async def scenario():
        booking = await _insert_booking(db_session)
        processed = await BookingService.process_booking(
            booking.id, db_session, should_fail=False
        )
        processed_again = await BookingService.process_booking(
            booking.id, db_session, should_fail=True
        )
        return booking, processed, processed_again

    booking, processed, processed_again = run(scenario())

    assert processed.status == consts.BookingStatus.CONFIRMED
    assert (
        processed.notification_log
        == f"Mock notification sent for booking {booking.id} to Worker Test"
    )
    assert processed_again.status == consts.BookingStatus.CONFIRMED
    assert processed_again.notification_log == processed.notification_log
    assert "mock_notification_sent" in caplog.text


def test_worker_marks_booking_failed_on_mock_external_failure(
    db_session: AsyncSession,
):
    async def scenario():
        booking = await _insert_booking(db_session)
        return await BookingService.process_booking(
            booking.id, db_session, should_fail=True
        )

    processed = run(scenario())

    assert processed.status == consts.BookingStatus.FAILED
    assert processed.notification_log is None
