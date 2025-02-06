import base64
import uvicorn
from fastapi import FastAPI, status, HTTPException
from os import listdir
from os.path import isfile, join, getctime

from utilities.file_handler import FileHandler
from api_models.api_models import ConfigModel
from core.camera import Camera
from core.sensor import UltrasonicSensor
from core.image_analyzer import ImageAnalyzer
from error_handling.errors import NotEnoughWater, CapturingDistanceError
from utilities.scheduler import Scheduler


app = FastAPI()

@app.get("/config", status_code=status.HTTP_200_OK)
async def get_config():
    """
    Retorna toda el archivo de configuracion del dispositivo.
    """
    fileHandler = FileHandler()
    config = fileHandler.read_config()
    if config is None:
        raise HTTPException(status_code=410, detail="No se pudo acceder al archivo de configuracion")
    return config
    
@app.patch("/basic-config", status_code=status.HTTP_200_OK)
async def update_basic_config(data: ConfigModel):
    """
    Permite parchear la configuracion basica del dispositivo. Esto incluye:
    ultrasound: (configuracion de la distancia que deberia tomar el sensor cuando el bebedero esta lleno o vacio)
        empty: int
        full: int
    volumetric: (Datos del bebedero, altura, profundidad y ancho)
        length: int
        height: int
        deep: int
    camera: (Cantidad de fotos que toma la camara por analisis)
        total_photo: int
    watertank: (Porcentaje de covertura necesaria que se busca aproximar a la hora de dosificar)
        coverage: int
    set_active: bool (Activar dosificador)
    reschedule_hours: (Horas antes de la siguiente dofisicacion en caso de error o en caso de funcionamiento normal)
        normal: int
        error: int
    """
    fileHandler = FileHandler()
    config = fileHandler.read_config()
    if config is None:
        raise HTTPException(status_code=410, detail="No se pudo acceder al archivo de configuracion")
    
    for config_field1, second_model in data.model_dump().items():
        if not isinstance(second_model, dict):
            if second_model is not None:
                config[config_field1] = second_model
            continue
        for config_field2, value in second_model.items():
            if value is not None:
                config[config_field1][config_field2] = value
    fileHandler.write(config)

@app.patch("/config", status_code=status.HTTP_200_OK)
async def update_config(data: dict):
    """
    Parchea la configuracion, permitiendo agregar datos nuevos aparte de la configuracion basica"""
    fileHandler = FileHandler()
    config = fileHandler.read_config()
    if config is None:
        raise HTTPException(status_code=410, detail="No se pudo acceder al archivo de configuracion")
    
    for config_field1, second_model in data.items():
        if not isinstance(second_model, dict):
            if second_model is not None:
                config[config_field1] = second_model
            continue
        for config_field2, value in second_model.items():
            if value is not None:
                config[config_field1][config_field2] = value
    fileHandler.write(config)
    return config


@app.get("/log/full", status_code=status.HTTP_200_OK)
async def get_log():
    """
    Retorna el log completo del sisitema"""
    fileHandler = FileHandler()
    log = fileHandler.read_log()
    if log is None:
        raise HTTPException(status_code=410, detail="No se pudo acceder al archivo del log")
    
    photos_path = FileHandler.photos
    photos = [f for f in listdir(photos_path) if isfile(join(photos_path, f))]
    imagenes = {}
    for photo in photos:
        with open(f"{photos_path}/{photo}", 'rb') as file:
            img_data = base64.b64encode(file.read()).decode("utf-8")
            imagenes[photo] = img_data
    resultado ={
        "log": log,
        "imagenes": imagenes
    }
    return resultado

@app.get("/log/text", status_code=status.HTTP_200_OK)
async def get_log_no_photo():
    """
    Retorna solo el texto del log en el dispositivo"""
    fileHandler = FileHandler()
    log = fileHandler.read_log()
    if log is None:
        raise HTTPException(status_code=410, detail="No se pudo acceder al archivo del log")
    resultado = {"log": log}
    return resultado

@app.get("/log/photos", status_code=status.HTTP_200_OK)
async def get_log_photos():
    """
    Retorna solo las fotos del log
    """
    photos_path = FileHandler.photos
    photos = [f for f in listdir(photos_path) if isfile(join(photos_path, f))]
    imagenes = {}
    for photo in photos:
        with open(f"{photos_path}/{photo}", 'rb') as file:
            img_data = base64.b64encode(file.read()).decode("utf-8")
            imagenes[photo] = img_data
    resultado ={
        "imagenes": imagenes
    }
    return resultado

@app.post("/camera/capture", status_code=status.HTTP_201_CREATED)
async def post_capture():
    """
    Saca una foto con la camara del dispositivo y devuelve la imagen y el nombre de esta (foto_manual.jpg)"""
    camera = Camera()
    if camera.camera is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="La camara ya esta en uso por otra aplicacion o hay un error con esta. Intentar mas tarde.")
    photo_path = camera.capture("foto_manual.jpg")
    camera.close()
    with open(photo_path, 'rb') as file:
        img_data = base64.b64encode(file.read()).decode("utf-8")
        result = {
            "nombre": "foto_manual.jpg",
            "imagen": img_data
        }
    return result

@app.get("/camera/last-image", status_code=status.HTTP_200_OK)
async def get_last_image():
    """
    Obtiene la ultima imagen tomada"""
    photos_path = FileHandler.photos
    photos = [f for f in listdir(photos_path) if isfile(join(photos_path, f))]
    oldest_file = max(photos, key=getctime)
    with open(photos_path + oldest_file, 'rb') as file:
        img_data = base64.b64encode(file.read()).decode("utf-8")
        result = {
            "imagen": img_data
        }
    return result

@app.get("/health", status_code=status.HTTP_200_OK)
async def get_health():
    """
    Obtiene la salud del dispotivo. Revisa si los sensores y los archivos funcionan correctamente"""
    try:
        sensor = UltrasonicSensor()
        sensor_result = sensor.distance()
        sensor.cleanup()
    except:
        sensor_result = None
    system_health = {}
    system_health["ultrasonic_sensor"] = True if sensor_result is not None else False

    try:
        camera = Camera()
        camera_result = camera.capture("test.jpg")
        camera.close()
    except:
        camera_result = None
    system_health["camera"] = True if camera_result is not None else False

    filehandler = FileHandler()
    config = filehandler.read_config()
    system_health["config"] = True if config is not None else False
    log = filehandler.read_log()
    system_health["log"] = True if log is not None else False

    return system_health

@app.get("/water-status", status_code=status.HTTP_200_OK)
async def get_water_status():
    """
    Analiza el estado del agua en el bebedero, devolviendo la distancia que tomo el sensor y la cantidad de agua estimada,
    a la vez que devuelve un error si se detecta que hay muy poca agua o algo obstruyendo el sensor."""
    fileHandler = FileHandler()
    config = fileHandler.read_config()
    try:
        sensor = UltrasonicSensor()
        result_sensor = sensor.run(config)
        result_dict = {
            "distancia": result_sensor[0],
            "nivel_de_agua": f"{result_sensor[1][0]}/{result_sensor[1][1]}",
            "error": None
        }
        sensor.cleanup()
        return result_dict
    except NotEnoughWater as e:
        result_dict = {
            "distancia": e.distance_data,
            "nivel_de_agua": f"{e.volumetric_result[0]}/{e.volumetric_result[1]}",
            "error": "No hay suficiente agua para hacer el analisis"
        }
        sensor.cleanup()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=result_dict)
    except CapturingDistanceError as e:
        result_dict = {
            "distancia": e.distance,
            "nivel_de_agua": None,
            "error": "Hay algo obstruyendo el sensor. La distancia tomada no es correcta"
        }
        sensor.cleanup()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=result_dict)
    except Exception as e:
        sensor.cleanup()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Hubo un error al acceder al sensor, no se pudieron obtener datos. Es posible que el sensor ya este en uso, intentelo de nuevo mas tarde.")


@app.get("/analyze/{photo_name}", status_code=status.HTTP_200_OK)
async def analyze_image(photo_name: str):
    """
    Analiza el porcentaje de covertura de una imagen especifica."""
    analyzer = ImageAnalyzer()
    path = FileHandler.photos + photo_name
    try:
        result = analyzer.calculate(path)
        return {
            "resultado": result
        }
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo analizar la imagen.")

@app.get("/analyze/last-image", status_code=status.HTTP_200_OK)
async def analyze_last_image():
    """
    Analiza la ultima foto tomada del dispositivo."""
    analyzer = ImageAnalyzer()
    photos_path = FileHandler.photos
    photos = [f for f in listdir(photos_path) if isfile(join(photos_path, f))]
    oldest_file = max(photos, key=getctime)
    path = photos_path + oldest_file
    try:
        result = analyzer.calculate(path)
        return {
            "resultado": result,
            "nombre": oldest_file
        }
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo analizar la imagen.")

@app.post("/scheduler/clear-jobs", status_code=status.HTTP_201_CREATED)
async def schedule_clear():
    """
    Elimina la lista de trabajos del dispositivo. Esto cancela todas las futuras dosificaciones planeadas."""
    scheduler = Scheduler()
    scheduler.clear()

@app.post("/scheduler/run-job", status_code=status.HTTP_201_CREATED)
async def schedule_run(script: str, minutes: int):
    """
    Agenda una dosificacion (si se ejecuta main.py) dentro de una cantidad de minutos especificadas.
    Se puede agendar la ejecucion de otro archivo si asi se desea."""
    scheduler = Scheduler()
    url = FileHandler.root + script
    scheduler.schedule_next_job(url=url, minutes=minutes)


@app.get("/")
def home():
    return {"message": "API funcionando en la red local"}

if __name__ == "__main__":
    pass