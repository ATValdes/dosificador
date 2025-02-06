import logging
from datetime import datetime
import os
from logging.handlers import TimedRotatingFileHandler
from utilities.file_handler import FileHandler

class Log:
    def __init__(self) -> None:
        self.filename = FileHandler.log
        format = logging.Formatter("%(levelname)s - %(asctime)s - %(message)s")
        logger = logging.getLogger()
        rotating_handler = TimedRotatingFileHandler(self.filename, backupCount=1)
        rotating_handler.setFormatter(format)
        logger.addHandler(rotating_handler)
        logger.setLevel(logging.DEBUG)
        self.logger = logger
        self.handler = rotating_handler

    def rotate_log_if_new_day(self):
        """
        Hace un rollOver cuando es el siguiente mes, queda la copia del ultimo mes. Encontrar forma de hacer que
        las imagenes esten conectadas al log de alguna forma
        """
        now = datetime.now().month
        file_date = datetime.fromtimestamp(os.path.getctime(f"{self.filename}")).month
        print(file_date, now)
        if file_date != now:
            self.logger.debug("Date changed with no events - rotating the log...")
            self.handler.doRollover()
            fileHandler = FileHandler()
            fileHandler.write_log_pictures_count(numero_fotos=0)
            fileHandler.delete_files("/home/pi/Desktop/dosificador/log_data/last_month_photos")
            fileHandler.cody_files("/home/pi/Desktop/dosificador/photos", "/home/pi/Desktop/dosificador/log_data/last_month_photos")
            fileHandler.delete_files("/home/pi/Desktop/dosificador/photos")
        
        

if __name__ == '__main__':
    log = Log()
    logger = log.logger
    logger.debug('debug message')
    logger.info('info message')
    log.rotate_log_if_new_day()
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')
