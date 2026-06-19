import datetime

import pydantic

from app.api.booking import consts


class BookingResponseSchemas(pydantic.BaseModel):
    id: int
    name: str
    appointment_at: datetime.datetime
    service_type: str
    status: consts.BookingStatus

    model_config = pydantic.ConfigDict(from_attributes=True, populate_by_name=True)


class CreateBookingRequestSchemas(pydantic.BaseModel):
    name: str = pydantic.Field(min_length=1, max_length=120)
    appointment_at: datetime.datetime = pydantic.Field(alias="datetime")
    service_type: str = pydantic.Field(min_length=1, max_length=80)

    model_config = pydantic.ConfigDict(populate_by_name=True)

    @pydantic.field_validator("appointment_at")
    @classmethod
    def appointment_must_be_future(cls, value: datetime.datetime) -> datetime.datetime:
        now = datetime.datetime.now(value.tzinfo or datetime.UTC)
        comparable = value if value.tzinfo else value.replace(tzinfo=datetime.UTC)
        if comparable <= now:
            raise ValueError("Booking datetime must be in the future")
        return value


class CreateBookingResponseSchemas(BookingResponseSchemas): ...


class ListBookingFilters(pydantic.BaseModel):
    status: consts.BookingStatus | None = None


class ListBookingRequestSchemas(pydantic.BaseModel):
    filters: ListBookingFilters | None = None
    order_by: consts.BookingOrderByType | None = consts.BookingOrderByType.CREATED_AT_DESC
    limit: int | None = pydantic.Field(default=10, ge=1, le=100)
    offset: int | None = pydantic.Field(default=0, ge=0)


class ListBookingResponseSchemas(pydantic.BaseModel):
    items: list[BookingResponseSchemas]
    total: int
    limit: int
    offset: int


class GetBookingResponseSchemas(BookingResponseSchemas): ...


class DeleteBookingResponseSchemas(pydantic.BaseModel):
    success: bool
