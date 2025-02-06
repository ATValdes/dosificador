import cv2
import numpy as np
import math
from datetime import datetime


class ImageAnalyzer:
    
	def loadValores(self, path, img, alto, ancho, plantillaBebedero):
		#camera.capture(pathCameraFoto)
		#img= cv2.imread(pathCameraFoto)
		img = cv2.imread(path)
		#imgTest = cv2.imread(pathCameraFoto)
		alto, ancho, _ = img.shape
		plantillaBebedero = np.zeros((alto, ancho, 3), dtype = "uint8")

	def dentroBebedero(self, plantilla, x, y):
		return (plantilla[y,x] > 0)


	def getPorcentajeCapsulas(self, imgParm, umbral):
		altoParm,anchoParm = imgParm.shape
		totalPixeles = anchoParm*altoParm
		pixelesCapsulas = 0
		
		for row in imgParm:
			for pixel in row:
				if (pixel >= umbral):
					pixelesCapsulas += 1
		
		return pixelesCapsulas / totalPixeles


	def getContornoMayor(self, contornos):
		contornoMayor = 0
		areaMayor = cv2.contourArea(contornos[0])
		for contorno in contornos:
			nuevaArea = cv2.contourArea(contorno)
			if (nuevaArea > areaMayor):
				areaMayor = nuevaArea
				contornoMayor = contorno
		
		return contornoMayor

	def GetCuadrantesCubiertos(self, mitadX, mitadY, line):
		cuadrantes = [False, False, False, False]
		if (line[0] < mitadX):
			if (line[1] < mitadY):
				cuadrantes[1] = True
			else:
				cuadrantes[2] = True
		else:
			if (line[1] < mitadY):
				cuadrantes[0] = True
			else:
				cuadrantes[3] = True
		if (line[2] < mitadX):
			if (line[3] < mitadY):
				cuadrantes[1] = True
			else:
				cuadrantes[2] = True
		else:
			if (line[3] < mitadY):
				cuadrantes[0] = True
			else:
				cuadrantes[3] = True
		count = 0
		for cuadrante in cuadrantes:
			if cuadrante:
				count+=1
		
		return count, cuadrantes

	def CheckIfExisteEn(self, arr, valoresARevisar):
		for i, arrVal in enumerate(arr):
			if (arrVal == valoresARevisar[i]):
				return True
		
		return False

	def GetIfDosLineasCubrenCadaCuadrante(self, lines, mitadX, mitadY):
		cuadrantes1 = [ False, False, False, False ]
		cuadrantes2 = [ False, False, False, False ]
		
		i = 0
		while(i < lines.__len__()):
			cantCuadrantes1, cuadrantes1 = self.GetCuadrantesCubiertos(mitadX, mitadY, lines[i][0])
			if (cantCuadrantes1 == 2):
				j = i + 1
				while(j < lines.__len__()):
					cantCuadrantes2, cuadrantes2 = self.GetCuadrantesCubiertos(mitadX, mitadY, lines[j][0])
					if (cantCuadrantes2 == 2 and not self.CheckIfExisteEn(cuadrantes1, cuadrantes2)):
						return True
					for k in [0,1,2,3]:
						cuadrantes2[k] = False
					j = j + 1
			for k in [0,1,2,3]:
				cuadrantes1[k] = False
			
			i = i + 1
		
		return False

	def Slope(self, x0, y0, x1, y1):
		return (y1-y0)/(x1-x0)

	def fullLine(self, img, a, b, color, ancho):
		slope = self.Slope(a[0], a[1], b[0], b[1])

		p = [0,0]
		q = [img.shape[1], img.shape[0]]	#q = (ancho de imagen, alto de imagen)

		p[1] = -(a[0] - p[0]) * slope + a[1]
		q[1] = -(b[0] - q[0]) * slope + b[1]
		
		r = (int(p[0]), int(p[1]))
		s = (int(q[0]), int(q[1]))

		cv2.line(img,r,s,color,ancho,cv2.LINE_AA)

	def GetHoughParameters(self, imgParm, imgParm1, imgParm2, anchoLinea):
		aux1 = cv2.GaussianBlur(imgParm, (7, 7), 0)
		
		# Edge detection
		imgHough1 = np.copy(imgParm)
		imgHough2 = np.copy(imgParm)

		imgCanny = cv2.Canny(aux1, 50, 200, 3)
		
		#Seteo inicial de variables
		threshold = 80
		maxThreshold = 256
		auxMax = 256
		imgParmAlto,imgParmAncho,_ = imgParm.shape
		if(imgParmAncho < imgParmAlto):	#Se asume que el bebedero ocupará un 65% del largo o ancho de la imagen
			minLineLength = imgParmAncho*0.55
		else:
			minLineLength = imgParmAlto * 0.55
		if(imgParmAncho < imgParmAlto):
			maxLineGap = imgParmAncho * 0.10
		else:
			maxLineGap = imgParmAlto * 0.10
		mitadX = (imgParm.shape)[1] / 2
		mitadY = imgParmAlto / 2

		linesP = cv2.HoughLinesP(imgCanny, 1, math.pi / 180, maxThreshold, None, minLineLength, maxLineGap)
		
		#Se halla el valor máximo de threshold que brinde suficientes resultados (al menos una linea cruzando dos cuadrantes, para ambos duos de cuadrantes)
		step = 128
		while (step > 10):
			if (linesP is None):
				maxThreshold = int(maxThreshold - step)
			else:
				if((linesP.__len__() < 4) or (not (self.GetIfDosLineasCubrenCadaCuadrante(linesP, mitadX, mitadY)))):
					maxThreshold = int(maxThreshold - step)
				else:
					#Posible máximo threshold
					auxMax = maxThreshold
					maxThreshold = int(maxThreshold + step)
			step = step / 2
			if(step > 10):
				linesP = cv2.HoughLinesP(imgCanny, 1, math.pi / 180, maxThreshold, None, minLineLength, maxLineGap)
		
		maxThreshold = auxMax

		#Ejecuta el analisis con las variables definitivas
		linesP = cv2.HoughLinesP(imgCanny, 1, math.pi / 180, maxThreshold, None, minLineLength, maxLineGap)

		#Dibuja las lineas del borde de la imagen a retornar 1
		imgParm1Alto,imgParm1Ancho,_ = imgParm1.shape
		imgParm1 = cv2.line(imgParm1, (0,0), (imgParm1Ancho - 1, 0), (255, 255, 255), anchoLinea, cv2.LINE_AA)
		imgParm1 = cv2.line(imgParm1, (0, 0), (0,imgParm1Alto - 1), (255, 255, 255), anchoLinea, cv2.LINE_AA)
		imgParm1 = cv2.line(imgParm1, (imgParm1Ancho- 1, 0), (imgParm1Ancho - 1, imgParm1Alto - 1), (255, 255, 255), anchoLinea, cv2.LINE_AA)
		imgParm1 = cv2.line(imgParm1, (0, imgParm1Alto - 1), (imgParm1Ancho - 1, imgParm1Alto - 1), (255, 255, 255), anchoLinea, cv2.LINE_AA)
		
		#Dibujo las lineas completas sin fin de extensión
		for line in linesP:
			self.fullLine(imgParm1, (line[0][0], line[0][1]),(line[0][2], line[0][3]),(255,255,255),anchoLinea)
			self.fullLine(imgHough1, (line[0][0], line[0][1]),(line[0][2], line[0][3]),(255,255,255),anchoLinea)
		
		#Dibuja las lineas del borde de la imagen a retornar 2
		imgParm2Alto,imgParm2Ancho, _ = imgParm2.shape
		cv2.line(imgParm2, (0, 0), (imgParm2Ancho - 1, 0), (255, 255, 255), anchoLinea, cv2.LINE_AA)
		cv2.line(imgParm2, (0, 0), (0, imgParm2Alto - 1), (255, 255, 255), anchoLinea, cv2.LINE_AA)
		cv2.line(imgParm2, (imgParm2Ancho - 1, 0), (imgParm2Ancho - 1, imgParm2Alto - 1), (255, 255, 255), anchoLinea, cv2.LINE_AA)
		cv2.line(imgParm2, (0, imgParm2Alto - 1), (imgParm2Ancho - 1, imgParm2Alto - 1), (255, 255, 255), anchoLinea, cv2.LINE_AA)
		
		#Dibuja las lineas encontradas de HoughLinesP
		for line in linesP:
			cv2.line(imgParm2, (line[0][0], line[0][1]), (line[0][2], line[0][3]), (255, 255, 255), anchoLinea, cv2.LINE_AA)
			cv2.line(imgHough2, (line[0][0], line[0][1]), (line[0][2], line[0][3]), (0, 0, 255), anchoLinea, cv2.LINE_AA)

		aux1 = cv2.normalize(imgParm1, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
		aux2 = cv2.normalize(imgParm2, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

		imgParm1 = cv2.cvtColor(aux1, cv2.COLOR_BGRA2GRAY)
		imgParm2 = cv2.cvtColor(aux2, cv2.COLOR_BGRA2GRAY)
		
		cv2.bitwise_not(imgParm1, aux1)
		cv2.bitwise_not(imgParm2, aux2)
		
		return aux1, aux2

	def GetPlantillaFromLineasRojas(self, imgLineasRojas, plantillaBebederoReducida):
		CannyLineasRojas = cv2.Canny(imgLineasRojas, 50, 200, 3)

		contornos, jerarquia = cv2.findContours(CannyLineasRojas, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		conPoly = []
		boundRect = []

		for i, contorno in enumerate(contornos):
			peri = cv2.arcLength(contorno, True)

			#Esta funcion cuenta la cantidad de vertices que encuentra en cada forma
			conPoly.append(cv2.approxPolyDP(contorno, 0.02 * peri, False))
			boundRect.append(cv2.boundingRect(conPoly[i]))
		
		contornoMayor = self.getContornoMayor(conPoly)

		#SE ASUME QUE EL CONTORNO DE MAYOR AREA ES EL CORRECTO
		#MAS ADELANTE PODRÍA ASEGURARSE MEJOR A PARTIR DE VERIFICAR SI TOCA EL PUNTO CENTRAL Y ATENDER SI NO LLEGA A SER EL CASO
		cv2.drawContours(plantillaBebederoReducida, [contornoMayor], -1, (255, 255, 255), cv2.FILLED)

		return plantillaBebederoReducida


	def getRectanguloInternoMaximo(self, plantilla, ladoMasExtenso):

		plantillaCanny = cv2.Canny(plantilla, 50, 200, 3)

		contornos, jerarquia = cv2.findContours(plantillaCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

		#Se asume que hay un solo contorno
		contorno = contornos[0]

		posiblesRectangulos = []
		
		#El rectangulo a hallar debe contener un tamaño mínimo asumiendo que se enfocó bien al bebedero, para reducir resultados a buscar
		areaMinAceptable = ladoMasExtenso * 0.4

		#Se listan todos los posibles rectangulos
		for i,puntos in enumerate(contorno):
			x1 = puntos[0][0]
			y1 = puntos[0][1]
			j = i + 1
			while (j < contorno.__len__()):
				x2 = contorno[j][0][0]
				y2 = contorno[j][0][1]
				area = abs(y2 - y1) * abs(x2 - x1)
				if(area > areaMinAceptable):
					posiblesRectangulos.append([[x1,y1], [x2,y2], area])
				j = j + 1

		#Se ordenan los rectangulos por tamaño
		posiblesRectangulosOrdenados = sorted(posiblesRectangulos, key=lambda rect: rect[2], reverse=True)
		
		#Se elije el primero que no tenga contacto con negro
		mejorRectEncontrada = False
		rectaValida = False
		i = 0
		cantRect = len(posiblesRectangulosOrdenados)
		rect = posiblesRectangulosOrdenados[0]
		while (not mejorRectEncontrada and i < cantRect):
			rect = posiblesRectangulosOrdenados[i]
			
			x1 = rect[0][0]
			y1 = rect[0][1]
			x2 = rect[1][0]
			y2 = rect[1][1]

			rectaValida = True
			xMax = max(x1, x2) - 1
			x = xMin = min(x1, x2) + 1
			yMax = max(y1, y2) - 1
			y = yMin = min(y1, y2) + 1

			while (rectaValida and x < xMax):
				if (plantilla[yMin, x] == 0 or plantilla[yMax, x] == 0):
					rectaValida = False
				x+= 1
			
			while (rectaValida and y < yMax):
				if (plantilla[y, xMin] == 0 or plantilla[y, xMax] == 0):
					rectaValida = False
				
				y+= 1
			
			if (rectaValida):
				mejorRectEncontrada = True
			else:
				i+= 1
		
		return [ posiblesRectangulosOrdenados[i][0], posiblesRectangulosOrdenados[i][1] ]

	def getGaborResults(self, imgParm):
		#Parametros de Gabor
		theetaArr = [ 1,2,3 ]
		sigmaArr = [ 1 ]
		lambdaArr = [ math.pi ]
		gammaArr = [ 1 ]
		ktype = cv2.CV_64F
		ksize = (11, 11)
		psi = 0

		#Inicializaciones extra
		imgParmGris = cv2.cvtColor(imgParm, cv2.COLOR_BGR2GRAY)
		imgParmAlto, imgParmAncho, _ = imgParm.shape

		result = np.zeros(imgParmGris.shape, dtype = "uint8")#cv2.Mat(imgParmAlto, imgParmAncho, cv2.CV_8UC1, [0])
		#Intentos
		for theeta in theetaArr:
			for sigma in sigmaArr:
				for lambdaVal in lambdaArr:
					for gamma in gammaArr:
						kernel = cv2.getGaborKernel(ksize, sigma, theeta, lambdaVal, gamma, psi, ktype)
						
						capsulas = cv2.filter2D(imgParmGris, cv2.CV_8UC3, kernel)
						
						_, capsulas = cv2.threshold(capsulas,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)

						result = result + capsulas

		return result

	def deleteBarrelEffect(self, src, ancho, alto):
		distCoeff = np.zeros((4,1),np.float64)

		# TODO: add your coefficients here!
		k1 = -1.5e-5; # negative to remove barrel distortion
		k2 = 0.0;
		p1 = 0.0;
		p2 = 0.0;

		distCoeff[0,0] = k1;
		distCoeff[1,0] = k2;
		distCoeff[2,0] = p1;
		distCoeff[3,0] = p2;

		# assume unit matrix for camera
		cam = np.eye(3,dtype=np.float32)

		cam[0,2] = ancho/2.0  # define center x
		cam[1,2] = alto/2.0 # define center y
		cam[0,0] = 10.        # define focal length x
		cam[1,1] = 10.        # define focal length y

		# here the undistortion will be computed
		dst = cv2.undistort(src,cam,distCoeff)
		
		return dst

	def contrastarImagen(self, imgParm):
		return cv2.convertScaleAbs(imgParm, alpha = 1.1, beta = 10)

	def calculate(self, path):
		alto = 0
		ancho = 0
		anchoLinea = 3
		tiempoInicio = datetime.now()
		img = cv2.imread(path)
		#imgTest = cv2.imread(pathCameraFoto)
		imgTest = cv2.imread(path)
		alto, ancho, _ = img.shape
		plantillaBebedero = np.zeros((alto, ancho, 3), dtype = "uint8")
		img = self.deleteBarrelEffect(img, ancho, alto)
		img = self.contrastarImagen(img)

		#Se reduce proporcionalmente la imagen para que su lado más extenso tenga 400 pixeles
		if(ancho > alto):
			ladoMasExtenso = ancho
			anchoNuevo = 400
			altoNuevo = 0
		else:
			ladoMasExtenso = alto
			altoNuevo = 400
			anchoNuevo = 0

		porcentajeReduccion = 400.0 / ladoMasExtenso

		if(altoNuevo == 0):
			altoNuevo = math.floor(alto * porcentajeReduccion)
		else:
			anchoNuevo = math.floor(ancho * porcentajeReduccion)

		imgReducida = cv2.resize(img, (anchoNuevo,altoNuevo), cv2.INTER_LINEAR)
		plantillaBebederoReducida = cv2.resize(plantillaBebedero, (anchoNuevo,altoNuevo), cv2.INTER_LINEAR)

		imgHough = np.zeros((altoNuevo,anchoNuevo,3))
		imgHoughP = np.zeros((altoNuevo,anchoNuevo,3))

		#Se busca los parámetros más apropiados para ejecutar Hough sobre la imagen para obtener el bebedero
		imgHough, imgHoughP = self.GetHoughParameters(imgReducida, imgHough, imgHoughP, anchoLinea)

		#Se obtiene la plantilla del bebedero a partir de la imagen creada por Hough
		plantillaBebederoReducida = self.GetPlantillaFromLineasRojas(imgHough, plantillaBebederoReducida)

		plantillaBebederoReducida = cv2.cvtColor(plantillaBebederoReducida, cv2.COLOR_BGR2GRAY)
		retval, plantillaBebederoReducida = cv2.threshold(plantillaBebederoReducida, 100, 255, cv2.THRESH_BINARY)

		#Se obtiene el rectangulo más grande capaz de contenerse dentro de la forma del bebedero
		rectMaxPlantillaReducida = self.getRectanguloInternoMaximo(plantillaBebederoReducida, ladoMasExtenso)

		rectMaxPlantillaReducida[0][0] = int(rectMaxPlantillaReducida[0][0])
		rectMaxPlantillaReducida[0][1] = int(rectMaxPlantillaReducida[0][1])
		rectMaxPlantillaReducida[1][0] = int(rectMaxPlantillaReducida[1][0])
		rectMaxPlantillaReducida[1][1] = int(rectMaxPlantillaReducida[1][1])

		plantillaBebederoReducida = cv2.rectangle(plantillaBebederoReducida, rectMaxPlantillaReducida[0], rectMaxPlantillaReducida[1], (155), -1)

		xMin = min(rectMaxPlantillaReducida[0][0], rectMaxPlantillaReducida[1][0])
		yMin = min(rectMaxPlantillaReducida[0][1], rectMaxPlantillaReducida[1][1])
		xMax = max(rectMaxPlantillaReducida[0][0], rectMaxPlantillaReducida[1][0])
		yMax = max(rectMaxPlantillaReducida[0][1], rectMaxPlantillaReducida[1][1])

		xMin = int(xMin/porcentajeReduccion)
		xMax = int(xMax/porcentajeReduccion)
		yMin = int(yMin/porcentajeReduccion)
		yMax = int(yMax/porcentajeReduccion)

		rectMaxBebedero = img[yMin:yMax,xMin:xMax]

		Capsulas = self.getGaborResults(rectMaxBebedero)
		elemKerelErode = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

		CapsulasBlur = cv2.dilate(Capsulas, elemKerelErode)

		porcentajeCapsulas = self.getPorcentajeCapsulas(CapsulasBlur, 125)

		tiempoFin = datetime.now()

		tiempoTardado = tiempoFin - tiempoInicio

		return (porcentajeCapsulas, tiempoTardado)

	def run(self, config, path):
     	#Analisis de cada imagen y promediar los resultados
		numero_foto = 1
		res_total = 0
		while numero_foto <= config["camera"]["total_photo"]:
			# path = '/home/pi/Desktop/%s.jpg' % numero_foto
			res = self.calculate(path)
			res_total = res_total + res[0]
			print(f"foto n° {numero_foto}: ")
			print("Porcentaje de cápsulas: " + str(res[0]))
			print("Tiempo tardado: ", res[1])
			numero_foto = numero_foto+1
		res_total = res_total / config["camera"]["total_photo"]
		return res_total


if __name__ == '__main__':
	#"/home/pi/Desktop/Tesis/Resources/TestingFinal/2023-03-05T00:17:54.129103.jpg"
	#"/home/pi/Desktop/Tesis/Resources/TestingFinal/2023-03-05T00:13:21.833310.jpg"
	#"/home/pi/Desktop/Tesis/Resources/TestingFinal/2023-03-05T00:17:25.208185.jpg"
	path = "./foto3	jpg"
	#"/home/pi/Desktop/Tesis/Resources/Vid_10_1.jpg"
	#"/home/pi/Desktop/Tesis/Resources/Prueba1.jpg"
	#'/home/pi/Desktop/Tesis/Resources/CajaBlanca.jpeg'#
	analizador = ImageAnalyzer()
	print(analizador.calculate(path))
 
	# alto = 0
	# ancho = 0
	# anchoLinea = 3
	# tiempoInicio = datetime.now()
	# img = cv2.imread(path)
	# #imgTest = cv2.imread(pathCameraFoto)
	# imgTest = cv2.imread(path)
	# alto, ancho, _ = img.shape
	# plantillaBebedero = np.zeros((alto, ancho, 3), dtype = "uint8")

	# img = deleteBarrelEffect(img, ancho, alto)
	# img = contrastarImagen(img)

	# #Se reduce proporcionalmente la imagen para que su lado más extenso tenga 400 pixeles

	# if(ancho > alto):
	# 	ladoMasExtenso = ancho
	# 	anchoNuevo = 400
	# 	altoNuevo = 0
	# else:
	# 	ladoMasExtenso = alto
	# 	altoNuevo = 400
	# 	anchoNuevo = 0

	# porcentajeReduccion = 400.0 / ladoMasExtenso

	# if(altoNuevo == 0):
	# 	altoNuevo = math.floor(alto * porcentajeReduccion)
	# else:
	# 	anchoNuevo = math.floor(ancho * porcentajeReduccion)

	# imgReducida = cv2.resize(img, (anchoNuevo,altoNuevo), cv2.INTER_LINEAR)
	# plantillaBebederoReducida = cv2.resize(plantillaBebedero, (anchoNuevo,altoNuevo), cv2.INTER_LINEAR)

	# imgHough = np.zeros((altoNuevo,anchoNuevo,3))
	# imgHoughP = np.zeros((altoNuevo,anchoNuevo,3))

	# #Se busca los parámetros más apropiados para ejecutar Hough sobre la imagen para obtener el bebedero
	# imgHough, imgHoughP = GetHoughParameters(imgReducida, imgHough, imgHoughP, anchoLinea)

	# #Se obtiene la plantilla del bebedero a partir de la imagen creada por Hough
	# plantillaBebederoReducida = GetPlantillaFromLineasRojas(imgHough, plantillaBebederoReducida)

	# plantillaBebederoReducida = cv2.cvtColor(plantillaBebederoReducida, cv2.COLOR_BGR2GRAY)
	# retval, plantillaBebederoReducida = cv2.threshold(plantillaBebederoReducida, 100, 255, cv2.THRESH_BINARY)

	# #Se obtiene el rectangulo más grande capaz de contenerse dentro de la forma del bebedero
	# rectMaxPlantillaReducida = getRectanguloInternoMaximo(plantillaBebederoReducida, ladoMasExtenso)

	# rectMaxPlantillaReducida[0][0] = int(rectMaxPlantillaReducida[0][0])
	# rectMaxPlantillaReducida[0][1] = int(rectMaxPlantillaReducida[0][1])
	# rectMaxPlantillaReducida[1][0] = int(rectMaxPlantillaReducida[1][0])
	# rectMaxPlantillaReducida[1][1] = int(rectMaxPlantillaReducida[1][1])

	# plantillaBebederoReducida = cv2.rectangle(plantillaBebederoReducida, rectMaxPlantillaReducida[0], rectMaxPlantillaReducida[1], (155), -1)

	# xMin = min(rectMaxPlantillaReducida[0][0], rectMaxPlantillaReducida[1][0])
	# yMin = min(rectMaxPlantillaReducida[0][1], rectMaxPlantillaReducida[1][1])
	# xMax = max(rectMaxPlantillaReducida[0][0], rectMaxPlantillaReducida[1][0])
	# yMax = max(rectMaxPlantillaReducida[0][1], rectMaxPlantillaReducida[1][1])

	# xMin = int(xMin/porcentajeReduccion)
	# xMax = int(xMax/porcentajeReduccion)
	# yMin = int(yMin/porcentajeReduccion)
	# yMax = int(yMax/porcentajeReduccion)

	# rectMaxBebedero = img[yMin:yMax,xMin:xMax]

	# Capsulas = getGaborResults(rectMaxBebedero)
	# elemKerelErode = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

	# CapsulasBlur = cv2.dilate(Capsulas, elemKerelErode)

	# porcentajeCapsulas = getPorcentajeCapsulas(CapsulasBlur, 125)

	# tiempoFin = datetime.now()

	# tiempoTardado = tiempoFin - tiempoInicio

	# print("Porcentaje de cápsulas:" + str(porcentajeCapsulas))
	# print("Tiempo tardado: ", tiempoTardado)
	
