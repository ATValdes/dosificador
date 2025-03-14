from fastapi import APIRouter, status
from api.controllers.config_controller import get_config, update_basic_config, update_config
from api.models.api_models import ConfigModel

router = APIRouter()

@router.get("/config", status_code=status.HTTP_200_OK)
async def get_config_route():
    """Retorna la configuración completa del sistema."""
    return get_config()

@router.patch("/basic-config", status_code=status.HTTP_200_OK)
async def update_basic_config_route(data: ConfigModel):
    """Permite actualizar configuraciones básicas del sistema."""
    update_basic_config(data)

@router.patch("/config", status_code=status.HTTP_200_OK)
async def update_config_route(data: dict):
    """Actualiza la configuración permitiendo agregar nuevos datos."""
    return update_config(data)
