import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Импортируем роутеры всех трех задач
from src.handlers.robinson import router as robinson_router
from src.handlers.star_visibility import router as star_router
from src.handlers.constellation_finder import router as constellation_router

app = FastAPI(title="Space Rescue API — Unified System")

# Подключаем эндпоинты задач
app.include_router(robinson_router)
app.include_router(star_router)
app.include_router(constellation_router)

# --- ОБРАБОТКА ОШИБОК ПО ТРЕБОВАНИЯМ ТЗ ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Возвращает 400 при любой ошибке валидации данных Pydantic.
    Это гарантирует ответ {'status': 'incorrect_input'} на плохой JSON.
    """
    return JSONResponse(
        status_code=400,
        content={"status": "incorrect_input"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Ловит любые непредвиденные системные ошибки.
    """
    return JSONResponse(
        status_code=400,
        content={"status": "incorrect_input"}
    )

if __name__ == "__main__":
    # Запуск на 0.0.0.0:8000 — критически важно для Docker-контейнера
    uvicorn.run(app, host="0.0.0.0", port=8000)
