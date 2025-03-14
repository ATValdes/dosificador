from datetime import datetime
from error_handling.troubleshooting import ErrorHandler
from core.image_analyzer import ImageAnalyzer
from core.sensor import UltrasonicSensor
from core.camera import Camera
from utilities.scheduler import Scheduler
from utilities.file_handler import FileHandler
from utilities.log import Log
from send_info.sendInfo import SendInfo

def workflow(config:dict, logger:Log, camera: Camera, sensor:UltrasonicSensor, analizador:ImageAnalyzer,
             error_handler:ErrorHandler, scheduler:Scheduler, main_path: str, sendInfo:SendInfo, time_of_script_init:datetime):

	# Limpia la lista de trabajos
	scheduler.clear()

	# Revisa que el sistema este configurado como activo, si no detiene la ejecucion y la programa para otro momento
	if not config["set_active"]:
		logger.logger.warning(f"La aplicacion no esta activa, volviendo a intentar dentro de {config['reschedule_hours']['normal']} horas")
		scheduler.schedule_next_job(main_path, hours=config['reschedule_hours']['normal'], time_of_script_init=time_of_script_init)
		return

	# Revisa la distancia del ultrasonido al agua y detecta si hay suficiente agua para realizar el analisis, sino, reprograma para otro momento.
	distance = error_handler.handle_sensor_errors(sensor)
	if distance is None:
		scheduler.schedule_next_job(main_path, hours=config['reschedule_hours']['error'], time_of_script_init=time_of_script_init)
		sendInfo.send_error(4,camera, sensor)
		return

	# Toma una serie de fotos y las analiza para medir el porcentaje de covertura de capsulas en el agua. Si alguna de las partes falla, se reprograma para otro momento.
	resultado = error_handler.handle_image_errors(camera, analizador)
	if resultado is None:
		scheduler.schedule_next_job(main_path, hours=config['reschedule_hours']['error'], time_of_script_init=time_of_script_init)
		sendInfo.send_error(4,camera, sensor)
		return

	print(f"Promedio: {resultado}")
	logger.logger.info(f"Analisis realizado con resultado promedio de {resultado}")

	covertura_objetivo = config["watertank"]["coverage"]/100
	rango_error_de_covertura = 0.1

	# Si el porcentaje no esta dentro del rango de covertura aceptable, empieza la dofisicacion.
	if resultado < (covertura_objetivo - rango_error_de_covertura):
		resultado_dosificar = error_handler.handle_dosification_errors(resultado, camera, analizador,
										   covertura_objetivo, tiempo=10, rango_error=rango_error_de_covertura)
		if resultado_dosificar is None:
			scheduler.schedule_next_job(main_path, hours=config['reschedule_hours']['error'], time_of_script_init=time_of_script_init)
			sendInfo.send_error(4,camera, sensor)
			return

	# Si no ocurre ningun error en la dosificacion, se vuelve a programar la re-ejecucion del programa para otro momento.
	scheduler.schedule_next_job(main_path, hours=config['reschedule_hours']['normal'], time_of_script_init=time_of_script_init)


if __name__ == '__main__':
	print("Inicio de main")
	# Guardo el tiempo cuando se ejecuto el programa. Esto es para poder reprogramar la ejecucion de este con mejor precision, dado
	# que el programa puede tardar varios minutos en ejecutarse y la reprogramacion sucede al final.
	time_of_script_init = datetime.now()

	fileHandler = FileHandler()
	config = fileHandler.read_config()

	#Crear clases necesarias
	logger = Log()
	logger.rotate_log_if_new_day()
	sensor = UltrasonicSensor()
	camera = Camera()
	analizador = ImageAnalyzer()
	error_handler = ErrorHandler(logger, config)
	scheduler = Scheduler()
	sendInfo = SendInfo()

	main_path = FileHandler.root + "main.py"

	workflow(config, logger, camera, sensor, analizador, error_handler, scheduler, main_path, sendInfo, time_of_script_init)
	sensor.cleanup()
