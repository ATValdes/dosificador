from error_handling.troubleshooting import ErrorHandler
from core.image_analyzer import ImageAnalyzer
from core.sensor import UltrasonicSensor
from core.camera import Camera
from utilities.scheduler import Scheduler
from utilities.file_handler import FileHandler
from utilities.log import Log
from send_info.sendInfo import SendInfo

def dosificar(config, resultado):
	#Luego del analisis del agua, se dosifica en caso de que falten capsultas.
	covertura_total = config["watertank"]["coverage"]/100
	if resultado < covertura_total:
		print(f"El porcentaje de covertura es de {resultado}/{covertura_total}")
		print("Todavia falta dosificar mas el agua para llevar al porcentaje requerido")
		#Script para dosificar

def workflow(config:dict, logger:Log, camera: Camera, sensor:UltrasonicSensor, analizador:ImageAnalyzer,
             error_handler:ErrorHandler, scheduler:Scheduler, main_path: str, sendInfo:SendInfo):

	scheduler.clear()
	if not config["set_active"]:
		logger.logger.warning(f"La aplicacion no esta activa, volviendo a intentar dentro de {config['reschedule_hours']['normal']} horas")
		scheduler.schedule_next_job(main_path, hours=config['reschedule_hours']['normal'])
		return

	distance = error_handler.handle_sensor_errors(sensor)
	if distance is None:
		scheduler.schedule_next_job(main_path, hours=config['reschedule_hours']['error'])
		sendInfo.send_error(4,camera, sensor)
		return

	resultado = error_handler.handle_image_errors(camera, analizador)
	if resultado is None:
		scheduler.schedule_next_job(main_path, hours=config['reschedule_hours']['error'])
		sendInfo.send_error(4,camera, sensor)
		return

	print(f"Promedio: {resultado}")
	logger.logger.info(f"Analisis realizado con resultado promedio de {resultado}")

	covertura_total = config["watertank"]["coverage"]/100
	if resultado < covertura_total:
		# EJECUTAR SCRIPT PARA DOSIFICAR
		print(f"El porcentaje de covertura es de {resultado}/{covertura_total}")
		print("Todavia falta dosificar mas el agua para llevar al porcentaje requerido")

	scheduler.schedule_next_job(main_path, hours=config['reschedule_hours']['normal'])


if __name__ == '__main__':
	print("Inicio de main")
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

	workflow(config, logger, camera, sensor, analizador, error_handler, scheduler, main_path, sendInfo)
	sensor.cleanup()
