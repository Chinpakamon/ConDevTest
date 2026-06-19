from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.booking import consts, rate_limit, schemas, service
from app.core.database.core import get_session

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post(
    "",
    response_model=schemas.CreateBookingResponseSchemas,
    dependencies=[Depends(rate_limit.check_post_rate_limit)],
)
async def create_booking(
    data: schemas.CreateBookingRequestSchemas,
    session: AsyncSession = Depends(get_session),
):
    return await service.BookingService.create_booking(
        data=data, session=session
    )


@router.get("", response_model=schemas.ListBookingResponseSchemas)
async def booking_list(
    status: consts.BookingStatus | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    order_by: consts.BookingOrderByType = Query(
        default=consts.BookingOrderByType.CREATED_AT_DESC
    ),
    session: AsyncSession = Depends(get_session),
):
    params = schemas.ListBookingRequestSchemas(
        filters=(
            schemas.ListBookingFilters(status=status)
            if status is not None
            else None
        ),
        limit=limit,
        offset=offset,
        order_by=order_by,
    )
    return await service.BookingService.get_booking_list(
        params=params, session=session
    )


@router.get(
    "/{booking_id:int}", response_model=schemas.GetBookingResponseSchemas
)
async def get_booking(
    booking_id: int, session: AsyncSession = Depends(get_session)
):
    return await service.BookingService.get_booking(
        booking_id=booking_id, session=session
    )


@router.delete(
    "/{booking_id:int}", response_model=schemas.DeleteBookingResponseSchemas
)
async def booking_delete(
    booking_id: int, session: AsyncSession = Depends(get_session)
):
    return await service.BookingService.delete_booking(
        booking_id=booking_id, session=session
    )
