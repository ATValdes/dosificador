from fastapi import APIRouter
from api.controllers.sensor_controller import get_water_status, get_health_status

router = APIRouter()

@router.get("/water-status")
async def get_water_status_route():
    """Devuelve el estado del agua en el bebedero."""
    return get_water_status()

@router.get("/health")
async def get_health_status_route():
    """Devuelve el estado de los sensores y del sistema."""
    return get_health_status()
