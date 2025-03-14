from fastapi import APIRouter
from api.controllers.analyze_controller import analyze_specific_image, analyze_last_image

router = APIRouter()

@router.get("/analyze/image/{photo_name}")
async def analyze_specific_image_route(photo_name: str):
    """Analiza una imagen especifica y devuelve su resultado."""
    return analyze_specific_image(photo_name)

@router.get("/analyze/last-image")
async def analyze_last_image_route():
    """Analiza la ultima imagen tomada y devuelve su resultado."""
    return analyze_last_image()
