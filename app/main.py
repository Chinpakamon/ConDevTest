from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from sqlalchemy import text

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
