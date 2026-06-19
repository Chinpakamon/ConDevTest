class BookingNotFoundException(Exception):
    """Raised when a booking does not exist."""


class BookingCannotBeCancelledException(Exception):
    """Raised when a booking is not pending anymore."""


class DatabaseException(Exception):
    """Database operation error."""
