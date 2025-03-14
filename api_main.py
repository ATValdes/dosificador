from fastapi import FastAPI
from api.routes import config, logs, camera, sensors, analyze, scheduler

app = FastAPI()

app.include_router(config.router)
app.include_router(logs.router)
app.include_router(camera.router)
app.include_router(sensors.router)
app.include_router(analyze.router)
app.include_router(scheduler.router)