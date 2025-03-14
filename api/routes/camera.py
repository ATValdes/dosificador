from fastapi import APIRouter, status
from api.controllers.camera_controller import capture_photo, get_last_image, get_photo

router = APIRouter()

@router.post("/camera/capture", status_code=status.HTTP_201_CREATED)
async def capture_photo_route():
    """Saca una foto con la camara y devuelve la imagen en base64."""
    return capture_photo()

@router.get("/camera/last-image", status_code=status.HTTP_200_OK)
async def get_last_image_route():
    """Obtiene la ultima imagen tomada."""
    return get_last_image()

@router.get("/camera/photo/{photo_name}")
async def get_photo_route(photo_name: str):
    """Obtiene una imagen específica por su nombre."""
    return get_photo(photo_name)