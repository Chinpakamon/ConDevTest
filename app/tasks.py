import asyncio
import logging
import random

from app.api.booking import service
from app.celery_app import celery_app
from app.core.database.core import SessionLocal
from app.core.settings import settings

logger = logging.getLogger(__name__)


async def process_booking_async(
    booking_id: int, *, failure_probability: float | None = None
) -> str:
    probability = (
        settings.booking_failure_probability
        if failure_probability is None
        else failure_probability
    )
    async with SessionLocal() as session:
        should_fail = random.random() < probability
        booking = await service.BookingService.process_booking(
            booking_id=booking_id,
            session=session,
            should_fail=should_fail,
        )
        logger.info(
            "booking_processed",
            extra={
                "booking_id": booking.id,
                "booking_status": booking.status.value,
            },
        )
        return booking.status.value


@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
)
def process_booking(self, booking_id: int) -> str:
    return asyncio.run(process_booking_async(booking_id))
