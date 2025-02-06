import time
from error_handling.errors import NotEnoughWater, CapturingDistanceError

class ErrorHandler:
	def __init__(self, logger, config):
		self.logger = logger.logger
		self.config = config

	def handle_sensor_errors(self, sensor, retries=3, delay=2):
		for attempt in range(retries):

			try:
				resultado = sensor.run(self.config)
				print(resultado)
				self.logger.info(f"Cantidad de agua aproximada en el bebedero {resultado[1][0]}/{resultado[1][1]}. Cantidad de agua adecuada para el analisis")
				return resultado[0]
			except NotEnoughWater as e:
				self.logger.error(f"Intento {attempt}: No hay suficiente agua para realizar un analisis. Cantidad de agua {e.volumetric_result[0]}/{e.volumetric_result[1]}")
				time.sleep(delay)
			except CapturingDistanceError as e:
				self.logger.error(f"Intento {attempt}: Error al medir la distancia al agua. La distancia tomada fue {e.distance}. Es demasiado cerca de sensor o se tomo una medida negativa.")
				time.sleep(delay)
			except Exception as e:
				self.logger.error(f"Intento {attempt}: Hubo un error no identificado al usar el sensor")
				time.sleep(delay)

		self.logger.error("Cantidad de intentos consumida, no se continuara con la dosificacion")
		return None

	def handle_image_errors(self, camera, analizador, retries=3, delay=2):
		if camera.camera is None:
			self.logger.error("No se puede acceder a la camara. El recurso ya esta en uso o tiene un error.")
			return None

		for attempt in range(retries):
			try:
				fotos_tomadas = camera.sacar_fotos(self.config)
				for foto_path in fotos_tomadas:
					self.logger.info(f"Se tomo una foto - {foto_path.split('/')[-1]}")
			except:
				self.logger.error("Error al tomar las fotos")
				return None

			try:
				resultados = []
				for foto in fotos_tomadas:
					resultado = analizador.run(self.config, foto)
					self.logger.info(f"Se analizo la foto {foto_path.split('/')[-1]} con un resultado de {resultado}")
					resultados.append(resultado)
				return sum(resultados)/len(resultados)
			except Exception as e:
				self.logger.error(f"Intento {attempt}: Hubo un error no identificado al intentar hacer un analisis de una imagenes. Imagen {foto_path.split('/')[-1]}")
				print("Error analizando imagen")
				time.sleep(delay)

		self.logger.error("Cantidad de intentos consumida, no se continuara con la dosificacion")
		return None
	
	@staticmethod
	def handle_file_errors(message: str):
		def decorator(func):
			def wrapper(*args, **kwargs):
				try:
					return func(*args, **kwargs)
				except:
					return None
				return None
			return wrapper
		return decorator
