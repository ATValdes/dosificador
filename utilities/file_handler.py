import yaml
import shutil
import os

class FileHandler:
    config =  "/home/pi/Desktop/dosificador/config.yml"
    log_pictures_count = "/home/pi/Desktop/dosificador/log_data/log_pictures_count.log"
    log = "/home/pi/Desktop/dosificador/log_data/logger.log"
    photos = "/home/pi/Desktop/dosificador/photos/"
    root = "/home/pi/Desktop/dosificador/"

    def read_log_pictures_count(self):
        with open(self.log_pictures_count, 'r') as file:
            numero_fotos = file.readline()
            print(f"Se abrio el archivo: {numero_fotos}")
        if numero_fotos:
            return int(numero_fotos)
        return 0

    def write_log_pictures_count(self, numero_fotos):
        with open(self.log_pictures_count, 'w') as file:
            file.write(str(numero_fotos))
        return 1
    
    def read_config(self):
        with open(self.config, 'r') as file:
            return yaml.safe_load(file)

    def write_config(self, data):
        with open(self.config, 'r') as file:
            yaml.dump(data, file, default_flow_style=False)
        return 1

    def read_log(self):
        print("hola")
        with open(self.log, 'r') as file:
            data = file.readlines()
        resultado = []
        for line in data:
            resultado.append(line)
        print(resultado)
        return resultado

    def cody_files(self, source_folder: str, dst_folder: str):
        if not os.path.exists(dst_folder):
           os.makedirs(dst_folder)
        for filename in os.listdir(source_folder):
            file_path_src = os.path.join(source_folder, filename)
            file_path_dst = os.path.join(dst_folder, filename)
            shutil.copy(file_path_src, file_path_dst)

    def delete_files(self, folder: str):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
