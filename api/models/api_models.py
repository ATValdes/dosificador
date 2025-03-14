from pydantic import BaseModel

class UltrasoundModel(BaseModel):
    empty: int = None
    full: int = None

class VolumetricModel(BaseModel):
    lenght: int = None
    height: int = None
    deep: int = None

class CameraModel(BaseModel):
    total_photo: int = None

class WatertankModel(BaseModel):
    coverage: int = None

class RescheduleHoursModel(BaseModel):
    normal: int = None
    error: int = None

class ConfigModel(BaseModel):
    ultrasound: UltrasoundModel = UltrasoundModel()
    volumetric: VolumetricModel = VolumetricModel()
    camera: CameraModel = CameraModel()
    watertank: WatertankModel = WatertankModel()
    set_active: bool = None
    reschedule_hours: RescheduleHoursModel = RescheduleHoursModel()


class RunJobModel(BaseModel):
    script: str
    minutes: int