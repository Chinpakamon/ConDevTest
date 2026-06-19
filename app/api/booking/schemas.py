import datetime
import pydantic

from app.api.booking import consts


class BookingResponseSchemas(pydantic.BaseModel):
    id: int
    name: str
    datetime: datetime.datetime = pydantic.Field(alias="appointment_at")
    service_type: str
    status: consts.BookingStatus

    model_config = pydantic.ConfigDict(from_attributes=True, populate_by_name=True)


class CreateBookingRequestSchemas(pydantic.BaseModel):
    name: str = pydantic.Field(min_length=1, max_length=120)
    datetime: datetime.datetime
    service_type: str = pydantic.Field(min_length=1, max_length=80)

    @pydantic.field_validator("datetime")
    @classmethod
    def appointment_must_be_future(cls, value: datetime.datetime) -> datetime.datetime:
        if value.timestamp() <= datetime.now(value.tzinfo).timestamp():
            raise ValueError("Booking datetime must be in the future")
        return value


class CreateBookingResponseSchemas(BookingResponseSchemas): ...


class ListBookingFilters(pydantic.BaseModel):
    name: str
    status: str


class ListBookingRequestSchemas(pydantic.BaseModel):
    filters: ListBookingFilters | None = None
    order_by: consts.BookingOrderByType | None = consts.BookingOrderByType.CREATED_AT_DESC
    limit: int | None = 10
    offset: int | None = 0


class ListBookingResponseSchemas(pydantic.BaseModel):
    items: list[BookingResponseSchemas]
    total: int
    limit: int
    offset: int


class GetBookingResponseSchemas(BookingResponseSchemas): ...


class DeleteBookingResponseSchemas(pydantic.BaseModel):
    success: bool
