import base64
from fastapi import HTTPException, status
from core.camera import Camera
from utilities.file_handler import FileHandler
from os import listdir
from os.path import isfile, join, getctime, exists

def capture_photo():
    """Toma una foto con la cámara y la devuelve en base64."""
    camera = Camera()
    if camera.camera is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La cámara ya está en uso o tiene un error. Intente más tarde."
        )
    
    photo_path = camera.capture("foto_manual.jpg")
    camera.close()

    with open(photo_path, 'rb') as file:
        img_data = base64.b64encode(file.read()).decode("utf-8")

    return {"nombre": "foto_manual.jpg", "imagen": img_data}

def get_last_image():
    """Obtiene la ultima imagen tomada`."""
    photos_path = FileHandler.photos
    photos = [f for f in listdir(photos_path) if isfile(join(photos_path, f))]
    
    if not photos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay imágenes disponibles.")

    last_file = max(photos, key=lambda x: getctime(join(photos_path, x)))
    file_path = join(photos_path, last_file)

    with open(file_path, 'rb') as file:
        img_data = base64.b64encode(file.read()).decode("utf-8")

    return {"nombre": last_file, "imagen": img_data}

def get_photo(photo_name: str):
    """Obtiene una imagen específica y la devuelve como `StreamingResponse`."""
    photos_path = FileHandler.photos
    file_path = join(photos_path, photo_name)

    # Verificar si el archivo existe y es una imagen
    if not exists(file_path) or not photo_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada.")

    with open(file_path, 'rb') as file:
        img_data = base64.b64encode(file.read()).decode("utf-8")

    return {"nombre": photo_name, "imagen": img_data}