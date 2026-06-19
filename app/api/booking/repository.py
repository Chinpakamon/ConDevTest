import logging

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.booking import consts, exceptions, schemas
from app.core.database import models

logger = logging.getLogger(__name__)


class BookingRepository:
    @staticmethod
    async def insert_booking(
        data: schemas.CreateBookingRequestSchemas,
        session: AsyncSession,
    ) -> models.Booking:
        booking = models.Booking(
            name=data.name,
            appointment_at=data.appointment_at,
            service_type=data.service_type,
            status=consts.BookingStatus.PENDING,
        )
        session.add(booking)
        try:
            await session.commit()
            await session.refresh(booking)
            return booking
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Database error occurred", exc_info=e)
            raise exceptions.DatabaseException("Database error") from e

    @staticmethod
    async def select_booking_by_id(
        booking_id: int,
        session: AsyncSession,
    ) -> models.Booking | None:
        query = sqlalchemy.select(models.Booking).where(models.Booking.id == booking_id)
        return await session.scalar(query)

    @staticmethod
    def bookings_filter(
        query: sqlalchemy.Select,
        data: schemas.ListBookingRequestSchemas,
    ) -> sqlalchemy.Select:
        if data.filters and data.filters.status is not None:
            query = query.where(models.Booking.status == data.filters.status)
        return query

    @staticmethod
    def bookings_order_by(
        query: sqlalchemy.Select,
        order_by: consts.BookingOrderByType | None,
    ) -> sqlalchemy.Select:
        booking_order = consts.BookingOrderByType
        order_mapping = {
            booking_order.CREATED_AT_ASC: models.Booking.created_at.asc(),
            booking_order.CREATED_AT_DESC: models.Booking.created_at.desc(),
            booking_order.NAME_ASC: models.Booking.name.asc(),
            booking_order.NAME_DESC: models.Booking.name.desc(),
        }
        return query.order_by(order_mapping.get(order_by, models.Booking.created_at.desc()))

    @staticmethod
    async def select_bookings(
        data: schemas.ListBookingRequestSchemas,
        session: AsyncSession,
    ) -> tuple[list[sqlalchemy.RowMapping], int]:
        query = sqlalchemy.select(models.Booking)
        query = BookingRepository.bookings_filter(query=query, data=data)

        count_query = sqlalchemy.select(sqlalchemy.func.count()).select_from(query.subquery())
        count_result = await session.execute(count_query)
        total = count_result.scalar_one()

        query = BookingRepository.bookings_order_by(query=query, order_by=data.order_by)
        query = query.limit(data.limit).offset(data.offset)

        try:
            result = await session.scalars(query)
            return list(result.all()), total
        except SQLAlchemyError as e:
            logger.error("Database error occurred", exc_info=e)
            raise exceptions.DatabaseException("Database error") from e

    @staticmethod
    async def update_booking_status(
        booking: models.Booking,
        session: AsyncSession,
        status: consts.BookingStatus,
        notification_log: str | None = None,
    ) -> models.Booking:
        booking.status = status
        if notification_log is not None:
            booking.notification_log = notification_log
        try:
            await session.commit()
            await session.refresh(booking)
            return booking
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Database error occurred", exc_info=e)
            raise exceptions.DatabaseException("Database error") from e
