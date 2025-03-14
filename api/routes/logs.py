from fastapi import APIRouter
from api.controllers.logs_controller import get_full_log, get_log_text, get_log_images

router = APIRouter()

@router.get("/log/full")
async def get_full_log_route():
    """Devuelve el log completo con imágenes en Base64."""
    return get_full_log()

@router.get("/log/text")
async def get_log_text_route():
    """Devuelve solo el texto del log."""
    return get_log_text()

@router.get("/log/photos")
async def get_log_images_route():
    """Devuelve todas las imágenes del log en un archivo ZIP."""
    return get_log_images()
