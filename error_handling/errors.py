class NotEnoughWater(Exception):
	def __init__(self, distance_data, volumetric_result, message="No hay suficiente agua para realizar un analisis"):
		self.distance_data = distance_data
		self.volumetric_result = volumetric_result
		super().__init__(message)

class CapturingDistanceError(Exception):
	def __init__(self, distance, message="Error al medir el la distacia al agua. Distancia negativa o demasiado cerca del sensor"):
		self.distance = distance
		super().__init__(message)
