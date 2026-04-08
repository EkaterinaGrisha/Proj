# Space Rescue API

Единое веб-приложение для 3 задач этапа.

## Эндпоинты

- `POST /api/v1/robinson_cruise`
- `POST /api/v1/star_visibility`
- `POST /api/v1/constellation_finder`

Сервер запускается на `0.0.0.0:8000`.

## Состав репозитория

- `src/` — исходный код приложения
- `.cm-token` — токен участника (одна строка)
- `instruction.md` — подробная инструкция ручного запуска
- `Dockerfile` — сборка контейнера
- `docker-compose.yml` — запуск из опубликованного образа
- `README.md` — описание проекта
