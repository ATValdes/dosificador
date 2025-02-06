from gpiozero import Button
from picamera import PiCamera
from datetime import datetime
from signal import pause
from utilities.file_handler import FileHandler


class Camera:
	def __init__(self) -> None:
		try:
			self.camera = PiCamera()
		except:
			self.camera = None
		self.path = FileHandler.photos

	def sacar_fotos(self, cfg):
		if self.camera is None:
			return None
		fileHandler = FileHandler()
		numero_fotos_archivo = fileHandler.read_log_pictures_count()
		numero_foto = 1
		path_fotos_sacadas = []
		#Saca una cantidad de fotos para hacer el analisis
		while numero_foto <= cfg["camera"]["total_photo"]:
			numero_fotos_archivo = numero_fotos_archivo + 1
			name = 'foto_%s.jpg' % numero_fotos_archivo
			path = self.path + name
			self.capture(name)
			numero_foto = numero_foto + 1
			path_fotos_sacadas.append(path)

		fileHandler.write_log_pictures_count(numero_fotos=numero_fotos_archivo)
		return path_fotos_sacadas

	def capture(self, name):
		if self.camera is None:
			return None
		self.camera.capture(self.path + name)
		return self.path + name

	def close(self):
		if self.camera is None:
			return False
		self.camera.close()

if __name__ == '__main__':
	left_button = Button(2)
	right_button = Button(3)
	camera = Camera()

	while(True):
		valor = input("s para grabar, d para foto")
		if valor == "s":
			camera.start_preview()
		if valor == "d":
			timestamp = datetime.now().isoformat()
			path = '/home/pi/Desktop/%s.jpg' % timestamp
			camera.capture(path)
		pause()
