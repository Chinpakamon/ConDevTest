import datetime

import sqlalchemy
from sqlalchemy import orm

from app.api.booking import consts
from app.core import database


class Booking(database.Base):
    __tablename__ = "bookings"

    id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger().with_variant(sqlalchemy.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    name: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(120), 
        nullable=False
    )
    appointment_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        index=True
    )
    service_type: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(80), 
        nullable=False
    )
    status: orm.Mapped[consts.BookingStatus] = orm.mapped_column(
        sqlalchemy.Enum(
            consts.BookingStatus, 
            name="booking_status", 
            values_callable=lambda enum: [item.value for item in enum]
        ),
        default=consts.BookingStatus.PENDING, 
        nullable=False, 
        index=True
    )
    notification_log: orm.Mapped[str | None] = orm.mapped_column(
        sqlalchemy.String(255), 
        nullable=True
    )
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.func.now()
    )
    updated_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.func.now(), 
        onupdate=sqlalchemy.func.now()
    )
