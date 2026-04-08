from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.schemas.constellation import ConstellationFinderRequest, ConstellationFinderResponse
from src.logic.constellations import solve_task_3

router = APIRouter(prefix="/api/v1", tags=["Constellations"])

@router.post("/constellation_finder", response_model=ConstellationFinderResponse)
async def find_constellation(request_data: dict):
    """
    Эндпоинт для поиска созвездия по заданному шаблону.
    1. Проверяет корректность входных данных (schemas).
    2. Кластеризует звезды и строит MST (logic).
    3. Сравнивает изоморфизм и относительные длины ребер.
    """
    try:
        # Валидируем входящий словарь через нашу Pydantic схему
        # Это поймает ошибки структуры графа (связность, циклы)
        validated_data = ConstellationFinderRequest(**request_data)
        
        # Вызываем основную логику решения
        result = solve_task_3(validated_data)
        
        return result

    except (ValidationError, ValueError, KeyError, TypeError):
        # Если данные не прошли валидацию или логика упала на некорректных индексах
        return JSONResponse(
            status_code=400,
            content={"status": "incorrect_input"}
        )
    except Exception:
        # Глобальный перехватчик для обеспечения стабильности по ТЗ
        return JSONResponse(
            status_code=400,
            content={"status": "incorrect_input"}
        )
