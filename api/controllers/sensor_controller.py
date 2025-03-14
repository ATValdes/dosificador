from fastapi import HTTPException, status
from os.path import join

from core.camera import Camera
from core.sensor import UltrasonicSensor
from core.image_analyzer import ImageAnalyzer
from utilities.file_handler import FileHandler
from error_handling.errors import NotEnoughWater, CapturingDistanceError

def get_water_status():
    """Obtiene el estado del agua en el bebedero y maneja errores de sensores."""
    file_handler = FileHandler()
    config = file_handler.read_config()

    if config is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo cargar la configuración")

    try:
        sensor = UltrasonicSensor()
        result_sensor = sensor.run(config)
        sensor.cleanup()

        return {
            "distancia": result_sensor[0],
            "nivel_de_agua": f"{result_sensor[1][0]}/{result_sensor[1][1]}",
            "error": None
        }
    except NotEnoughWater as e:
        sensor.cleanup()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "distancia": e.distance_data,
                "nivel_de_agua": f"{e.volumetric_result[0]}/{e.volumetric_result[1]}",
                "error": "No hay suficiente agua para hacer el análisis"
            }
        )
    except CapturingDistanceError as e:
        sensor.cleanup()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "distancia": e.distance,
                "nivel_de_agua": None,
                "error": "Hay algo obstruyendo el sensor. La distancia tomada no es correcta"
            }
        )
    except Exception:
        sensor.cleanup()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hubo un error al acceder al sensor. Es posible que el sensor ya esté en uso, intentelo más tarde."
        )

def get_health_status():
    """Verifica la salud del dispotivo. Revisa si los sensores y los archivos funcionan correctamente"""
    try:
        sensor = UltrasonicSensor()
        sensor_result = sensor.distance()
        sensor.cleanup()
    except:
        sensor_result = None

    try:
        camera = Camera()
        camera_result = camera.capture("test.jpg")
        camera.close()
    except:
        camera_result = None
    
    try:
        if camera_result is None:
            analyze_result = None
        analyzer = ImageAnalyzer()
        analyze_result = analyzer.calculate(join(FileHandler.photos, camera_result))
    except:
        analyze_result = None

    system_health = {}
    system_health["ultrasonic_sensor"] = True if sensor_result is not None else False
    system_health["camera"] = True if camera_result is not None else False
    system_health["analyzer"] = True if analyze_result is not None else False

    try:
        filehandler = FileHandler()
        config = filehandler.read_config()
    except Exception as e:
        config = None
    system_health["config"] = True if config is not None else False

    try:
        log = filehandler.read_log()
    except Exception as e:
        log = None
    system_health["log"] = True if log is not None else False

    return system_health