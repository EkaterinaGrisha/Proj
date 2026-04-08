from fastapi import APIRouter
from src.schemas.star import StarVisibilityRequest, StarVisibilityResponse
from src.logic.astronomy import StarSystemSimulator, find_transmission_window

router = APIRouter(prefix="/api/v1", tags=["Astronomy"])

@router.post("/star_visibility", response_model=StarVisibilityResponse)
async def star_visibility(data: StarVisibilityRequest):
    """
    Эндпоинт для поиска окна связи со звездой.
    Использует физический симулятор для моделирования движения тел.
    """
    # Инициализация симулятора с данными из запроса
    simulator = StarSystemSimulator(
        bodies=data.celestial_bodies,
        target_star_vector=data.target_star_vector
    )
    
    # Поиск первого подходящего временного интервала
    start_wait, duration = find_transmission_window(
        simulator=simulator,
        required_time=data.observation_params.required_transmission_time
    )
    
    if start_wait is not None:
        return {
            "found": True,
            "next_fitting_interval_in": start_wait,
            "interval_duration": duration
        }
    
    return {"found": False}
