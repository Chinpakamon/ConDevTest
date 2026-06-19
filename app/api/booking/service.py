import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.booking import exceptions, repository, schemas
from app.core.database import models


logger = logging.getLogger(__name__)


class BookingService:

    @staticmethod
    async def _get_booking_or_raise(
        booking_id: int,
        session: AsyncSession,
    ) -> models.Booking:
        booking = await repository.BookingRepository.select_booking_by_id(
            booking_id=booking_id,
            session=session,
        )
        if not booking:
            raise exceptions.BookingNotFoundException()
        return booking


    @staticmethod
    async def get_booking(
        booking_id: int,
        session: AsyncSession,
    ) -> schemas.GetBookingResponseSchemas:
        booking = await BookingService._get_booking_or_raise(
            booking_id=booking_id,
            session=session,
        )
        return schemas.GetBookingResponseSchemas.model_validate(booking)


    @staticmethod
    async def get_booking_list(
        data: schemas.ListBookingRequestSchemas,
        session: AsyncSession,
    ) -> schemas.ListBookingResponseSchemas:
        bookings, total = await repository.BookingRepository.select_bookings(
            data=data,
            session=session,
        )
        return schemas.ListBookingResponseSchemas(
            data=[
                schemas.BookingResponseSchemas(**booking) for booking in bookings
            ],
            total=total,
            limit=data.limit,
            offset=data.offset,
        )
