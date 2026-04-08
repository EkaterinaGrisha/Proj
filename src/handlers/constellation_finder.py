from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.logic.constellations import solve_task_3
from src.schemas.constellation import ConstellationFinderRequest, ConstellationFinderResponse

router = APIRouter(prefix="/api/v1", tags=["Constellations"])


@router.post("/constellation_finder", response_model=ConstellationFinderResponse)
async def find_constellation(request_data: ConstellationFinderRequest):
    """
    Эндпоинт для поиска созвездия по заданному шаблону.
    """
    try:
        return solve_task_3(request_data)
    except Exception:
        return JSONResponse(status_code=400, content={"status": "incorrect_input"})
