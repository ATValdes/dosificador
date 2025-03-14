from fastapi import HTTPException, status
from utilities.file_handler import FileHandler
from api.models.api_models import ConfigModel

def get_config():
    """Obtiene la configuración completa del sistema."""
    file_handler = FileHandler()
    config = file_handler.read_config()
    if config is None:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="No se pudo acceder al archivo de configuración")
    return config

def update_basic_config(data: ConfigModel):
    """
    Actualiza solamente la configuracion básicas del sistema.

    La configuracion basica es la siguiente.
    
    ultrasound: (configuracion de la distancia que deberia tomar el sensor cuando el bebedero esta lleno o vacio)
        empty: int
        full: int
    volumetric: (Datos del bebedero, altura, profundidad y ancho)
        length: int
        height: int
        deep: int
    camera: (Cantidad de fotos que toma la camara por analisis)
        total_photo: int
    watertank: (Porcentaje de covertura necesaria que se busca aproximar a la hora de dosificar)
        coverage: int
    set_active: bool (Activar dosificador)
    reschedule_hours: (Horas antes de la siguiente dofisicacion en caso de error o en caso de funcionamiento normal)
        normal: int
        error: int
    """
    file_handler = FileHandler()
    config = file_handler.read_config()
    if config is None:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="No se pudo acceder al archivo de configuración")

    for config_field1, second_model in data.model_dump().items():
        if not isinstance(second_model, dict):
            if second_model is not None:
                config[config_field1] = second_model
            continue
        for config_field2, value in second_model.items():
            if value is not None:
                config[config_field1][config_field2] = value

    file_handler.write_config(config)

def update_config(data: dict):
    """Actualiza la configuracion permitiendo agregar datos nuevos."""
    fileHandler = FileHandler()
    config = fileHandler.read_config()
    if config is None:
        raise HTTPException(status_code=410, detail="No se pudo acceder al archivo de configuracion")
    
    for config_field1, config_change in data.items():
        if not isinstance(config_change, dict):
            config[config_field1] = config_change
            continue
        # Si el valor que se esta cambiando en la configuracion no es nuevo y es un dict, entonces se hace el cambio
        # sino se agrega como elemento nuevo
        if config_field1 in config.keys() and isinstance(config[config_field1], dict):
            for config_field2, value in config_change.items():
                config[config_field1][config_field2] = value
        else:
            config[config_field1] = config_change
    fileHandler.write_config(config)
    return config
