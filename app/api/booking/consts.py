import enum


class BookingStatus(enum.StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class BookingOrderByType(enum.StrEnum):
    CREATED_AT_ASC = "CREATED_AT_ASC"
    CREATED_AT_DESC = "CREATED_AT_DESC"
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"
