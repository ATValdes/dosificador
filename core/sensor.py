#Libraries
import RPi.GPIO as GPIO
import time

from error_handling.errors import CapturingDistanceError, NotEnoughWater
 
class UltrasonicSensor:
    def __init__(self, GPIO_TRIGGER=18, GPIO_ECHO=24):
        self.ultima_distancia = None

        #GPIO Mode (BOARD / BCM)
        self.EMPTY = 0
        self.HALF = 1
        self.FULL = 2

        GPIO.setmode(GPIO.BCM)
         
        #set GPIO Pins
        self.GPIO_TRIGGER = 18
        self.GPIO_ECHO = 24
         
        #set GPIO direction (IN / OUT)
        GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(GPIO_ECHO, GPIO.IN)
        
    def distance(self):
        # set Trigger to HIGH
        GPIO.output(self.GPIO_TRIGGER, True)
     
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.GPIO_TRIGGER, False)
     
        StartTime = time.time()
        StopTime = time.time()
        # save StartTime
        while GPIO.input(self.GPIO_ECHO) == 0:
            StartTime = time.time()
            
     
        # save time of arrival 6     
        while GPIO.input(self.GPIO_ECHO) == 1:
            StopTime = time.time()
     
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2
     
        return distance

    def cleanup(self):
        GPIO.cleanup()
    
    def is_there_enough_water(self, distance, cfg):
        empty = cfg['ultrasound']['empty']
        full = cfg['ultrasound']['full']
        empty_quarter = (empty - full)*75/100

        if distance >= empty_quarter:
            return False
        return True

    def volumetric_calc(self, dst, cfg):
        distance = dst - cfg['ultrasound']['full']
        total = (cfg['volumetric']['length']/100 * cfg['volumetric']['height']/100 * cfg['volumetric']['deep']/100) * 1000
        result = total - ((cfg['volumetric']['length']/100 * cfg['volumetric']['height']/100 * distance/100) * 1000)
        return (result, total)

    def run(self, cfg):
        distance = self.distance()
        
        # Demasiado cerca o valor negativo
        if distance < 10:
            raise CapturingDistanceError(distance)
        
        volumetric_result = self.volumetric_calc(distance, cfg)
        enough_water = self.is_there_enough_water(distance, cfg)
        #print (distance_result)
        
        # La distancia es demasiado larga, se asume que no hay suficiente agua en el bebedero
        if enough_water is False:
            raise NotEnoughWater(distance, volumetric_result)
        self.ultima_distancia = distance
        return distance, volumetric_result


if __name__ == '__main__':
    sensor = UltrasonicSensor()
    try:
        while True:
            dist = sensor.distance()
            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(1)
 
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        sensor.cleanup()
