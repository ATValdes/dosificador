import os
from fastapi import HTTPException, status
from utilities.scheduler import Scheduler
from utilities.file_handler import FileHandler
from api.models.api_models import RunJobModel

def clear_jobs():
    """Elimina todas las tareas programadas en el dispositivo."""
    try:
        scheduler = Scheduler()
        scheduler.clear()
        return {"message": "Todas las tareas programadas han sido eliminadas."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al limpiar tareas: {str(e)}")

def schedule_run(data: RunJobModel):
    """Programa la ejecucion de un script en una cantidad de minutos especifica."""
    if data.minutes <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El tiempo debe ser mayor a 0 minutos.")

    # Validar si el script existe
    script_path = os.path.join(FileHandler.root, data.script)
    if not os.path.exists(script_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El script '{data.script}' no existe.")

    try:
        scheduler = Scheduler()
        scheduler.schedule_next_job(url=script_path, minutes=data.minutes)
        return {"message": f"Se ha programado '{data.script}' para ejecutarse en {data.minutes} minutos."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al programar tarea: {str(e)}")

def schedule_list():
    """Lista de trabajos pendientes del dispositivo."""
    scheduler = Scheduler()
    result = scheduler.list_scheduled_jobs()

    return {"lista": result}
