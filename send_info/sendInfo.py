import base64

from utilities.file_handler import FileHandler


class SendInfo:
    def send_error(self, last_messages:int, camera, sensor):
        fileHandler = FileHandler()
        log = fileHandler.read_log()
        print(log)
        photos_path = fileHandler.photos
        res_log = []
        images = {}
        if len(log) > last_messages:
            count = last_messages
        else:
            count = len(log)
        for number in range(count-1, -1, -1):
            print(number)
            position = len(log)-1 - number
            log_data = log[position]
            photo = log_data.split(" ")[-1]
            photo = photo.strip("\n")
            print(photo)
            if ".jpg" in photo or ".png" in photo:
                with open(f"{photos_path}/{photo}", 'rb') as file:
                    img_data = base64.b64encode(file.read()).decode("utf-8")
                    images[photo] = img_data
            res_log.append(log_data)
        try:
            camera.capture("ultima_foto.jpg")
            with open(f"{photos_path}/{'ultima_foto.jpg'}", 'rb') as file:
                    img_data = base64.b64encode(file.read()).decode("utf-8")
                    images["ultima_foto"] = img_data
        except:
            images["ultima_foto"] = None
        self.send(log_data=res_log, imagenes=images, ultima_distancia=sensor.ultima_distancia)
    
    def send(self, log_data, imagenes:dict, ultima_distancia):
        print(log_data)
        # print(imagenes)
    
    def send_message(self, message: str):
        print(message)

if __name__ == "__main__":
    sendInfo = SendInfo()
    sendInfo.send_error(5)