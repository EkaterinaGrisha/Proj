from fastapi import APIRouter
from src.schemas.shuttle import MissionData, MissionResponse
from src.logic.navigation import find_optimal_path

router = APIRouter(prefix="/api/v1", tags=["Robinson"])

@router.post("/robinson_cruise", response_model=MissionResponse)
async def robinson_cruise(data: MissionData):
    """
    Эндпоинт для расчета оптимального пути спасения Робинзона.
    Логика расчета инкапсулирована в модуле navigation.
    """
    result = find_optimal_path(data)
    return result
