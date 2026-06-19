from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.booking import schemas, service
from app.core.database.core import get_session

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=schemas.CreateBookingResponseSchemas)
async def create_booking(
    data: schemas.CreateBookingRequestSchemas,
    session: AsyncSession = Depends(get_session)
):
    return await service.BookingService.create_booking(data=data, session=session)


@router.get("", response_model=schemas.ListBookingResponseSchemas)
async def booking_list(
    data: schemas.ListBookingRequestSchemas = Body(),
    session: AsyncSession = Depends(get_session)
):
    return await service.BookingService.get_booking_list(data=data, session=session)


@router.get("/{booking_id:int}", response_model=schemas.GetBookingResponseSchemas)
async def get_booking(
    booking_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await service.BookingService.get_booking(booking_id=booking_id, session=session)


@router.delete("/{booking_id:int}", response_model=schemas.DeleteBookingResponseSchemas)
async def booking_delete(
    booking_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await service.BookingService.delete_booking(booking_id=booking_id, session=session)
