import os
import base64
from fastapi import HTTPException
from utilities.file_handler import FileHandler
from os import listdir
from os.path import isfile, join
from starlette.responses import StreamingResponse
from io import BytesIO
import zipfile


def get_full_log():
    """Devuelve el log completo con imágenes en Base64."""
    file_handler = FileHandler()
    log = file_handler.read_log()
    
    if log is None:
        raise HTTPException(status_code=410, detail="No se pudo acceder al archivo del log")

    photos_path = FileHandler.photos
    if not os.path.exists(photos_path):
        raise HTTPException(status_code=404, detail="No se encontraron imágenes")

    # Obtener todas las imágenes disponibles
    photos = [f for f in listdir(photos_path) if isfile(join(photos_path, f))]
    imagenes = {}
    
    for photo in photos:
        file_path = join(photos_path, photo)
        with open(file_path, "rb") as file:
            img_data = base64.b64encode(file.read()).decode("utf-8")
            imagenes[photo] = img_data

    return {"log": log, "imagenes": imagenes}

def get_log_text():
    """Devuelve solo el texto del log."""
    file_handler = FileHandler()
    log = file_handler.read_log()
    
    if log is None:
        raise HTTPException(status_code=410, detail="No se pudo acceder al archivo del log")

    return {"log": log}

def get_log_images():
    """Devuelve todas las imagenes del log en un ZIP."""
    photos_path = FileHandler.photos
    
    if not os.path.exists(photos_path):
        raise HTTPException(status_code=404, detail="No se encontraron imagenes")

    photos = [f for f in listdir(photos_path) if isfile(join(photos_path, f)) and f.lower().endswith(('.jpg', '.png'))]

    if not photos:
        raise HTTPException(status_code=404, detail="No hay imagenes disponibles en el log")

    # Crear un ZIP en memoria con las imagenes
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for photo in photos:
            file_path = join(photos_path, photo)
            zip_file.write(file_path, arcname=photo)

    zip_buffer.seek(0)

    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=log_imagenes.zip"})
