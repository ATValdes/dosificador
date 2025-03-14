from fastapi import APIRouter, status

from api.controllers.scheduler_controller import clear_jobs, schedule_run, schedule_list
from api.models.api_models import RunJobModel

router = APIRouter()

@router.post("/scheduler/clear-jobs")
async def clear_jobs_route():
    """Elimina todas las tareas programadas en el dispositivo."""
    return clear_jobs()

@router.post("/scheduler/run-job")
async def schedule_run_route(data: RunJobModel):
    """Programa la ejecución de un script en una cantidad de minutos especifica."""
    return schedule_run(data)

@router.get("/scheduler/list-jobs", status_code=status.HTTP_201_CREATED)
async def schedule_list_route():
    """Lista todos los programas en la lista de ejecucion programada"""
    return schedule_list()