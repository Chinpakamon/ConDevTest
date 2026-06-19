import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app import tasks
from app.api.booking import consts, exceptions, repository, schemas
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
    async def create_booking(
        data: schemas.CreateBookingRequestSchemas,
        session: AsyncSession,
    ) -> schemas.CreateBookingResponseSchemas:
        booking = await repository.BookingRepository.insert_booking(
            data=data, session=session
        )
        tasks.process_booking.delay(booking.id)
        return schemas.CreateBookingResponseSchemas.model_validate(booking)

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
        params: schemas.ListBookingRequestSchemas,
        session: AsyncSession,
    ) -> schemas.ListBookingResponseSchemas:
        bookings, total = await repository.BookingRepository.select_bookings(
            params=params,
            session=session,
        )
        return schemas.ListBookingResponseSchemas(
            items=[
                schemas.BookingResponseSchemas.model_validate(booking)
                for booking in bookings
            ],
            total=total,
            limit=params.limit,
            offset=params.offset,
        )

    @staticmethod
    async def delete_booking(
        booking_id: int,
        session: AsyncSession,
    ) -> schemas.DeleteBookingResponseSchemas:
        booking = await BookingService._get_booking_or_raise(
            booking_id=booking_id, session=session
        )
        if booking.status != consts.BookingStatus.PENDING:
            raise exceptions.BookingCannotBeCancelledException()
        await repository.BookingRepository.update_booking_status(
            booking=booking,
            session=session,
            status=consts.BookingStatus.CANCELLED,
        )
        return schemas.DeleteBookingResponseSchemas(success=True)

    @staticmethod
    async def process_booking(
        booking_id: int,
        session: AsyncSession,
        *,
        should_fail: bool,
    ) -> models.Booking:
        booking = await BookingService._get_booking_or_raise(
            booking_id=booking_id, session=session
        )
        if booking.status != consts.BookingStatus.PENDING:
            logger.info(
                "booking_processing_skipped",
                extra={
                    "booking_id": booking.id,
                    "booking_status": booking.status.value,
                },
            )
            return booking
        if should_fail:
            return await repository.BookingRepository.update_booking_status(
                booking=booking,
                session=session,
                status=consts.BookingStatus.FAILED,
            )
        notification_log = f"Mock notification sent for booking {booking.id} to {booking.name}"
        logger.info(
            "mock_notification_sent",
            extra={
                "booking_id": booking.id,
                "service_type": booking.service_type,
            },
        )
        return await repository.BookingRepository.update_booking_status(
            booking=booking,
            session=session,
            status=consts.BookingStatus.CONFIRMED,
            notification_log=notification_log,
        )
