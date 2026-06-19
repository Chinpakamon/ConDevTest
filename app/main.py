from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.booking import exceptions
from app.api.booking.router import router as booking_router
from app.core.database.core import engine
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connected")
    except Exception as e:
        print("Database connection failed")
        raise e

    yield

    await engine.dispose()
    print("Database connections closed")


def create_app(*, enable_lifespan: bool = True) -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="Beauty API",
        version="1.0.0",
        lifespan=lifespan if enable_lifespan else None,
    )

    app.include_router(booking_router)

    @app.exception_handler(exceptions.BookingNotFoundException)
    async def booking_not_found_handler(
        request: Request, exc: exceptions.BookingNotFoundException
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Booking not found"},
        )

    @app.exception_handler(exceptions.BookingCannotBeCancelledException)
    async def booking_cannot_be_cancelled_handler(
        request: Request, exc: exceptions.BookingCannotBeCancelledException
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Only pending bookings can be cancelled"},
        )

    @app.exception_handler(exceptions.DatabaseException)
    async def database_exception_handler(
        request: Request, exc: exceptions.DatabaseException
    ):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database error"},
        )

    @app.get(
        "/health",
        tags=["Healthcheck"],
        status_code=status.HTTP_200_OK,
    )
    async def healthcheck():
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return {"status": "ok", "database": "ok"}
        except Exception:
            return {"status": "degraded", "database": "error"}

    return app


app = create_app()
