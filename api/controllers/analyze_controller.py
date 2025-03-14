from os import listdir
from os.path import getctime, join, exists, isfile
from fastapi import HTTPException, status

from core.image_analyzer import ImageAnalyzer
from utilities.file_handler import FileHandler

def analyze_specific_image(photo_name: str):
    """Analiza una imagen específica y devuelve su resultado."""
    analyzer = ImageAnalyzer()
    photos_path = FileHandler.photos
    file_path = join(photos_path, photo_name)

    if not exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada.")

    try:
        result = analyzer.calculate(file_path)
        return {"resultado": result, "nombre": photo_name}
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo analizar la imagen.")

def analyze_last_image():
    """Analiza la última imagen tomada y devuelve su resultado."""
    analyzer = ImageAnalyzer()
    photos_path = FileHandler.photos

    if not exists(photos_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directorio de imagenes no encontrado.")

    photos = [f for f in listdir(photos_path) if isfile(join(photos_path, f))]

    if not photos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay imagenes disponibles para analizar.")

    # Obtener la imagen más reciente
    last_file = max(photos, key=lambda x: getctime(join(photos_path, x)))
    file_path = join(photos_path, last_file)

    try:
        result = analyzer.calculate(file_path)
        return {"resultado": result, "nombre": last_file}
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo analizar la imagen.")
