import fastapi


class BookingNotFoundException(fastapi.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )


class BookingCannotBeCancelledException(fastapi.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Booking cannot be cancelled",
        )
