# Инструкция по ручному запуску

Ниже приведена пошаговая инструкция для ручной проверки решения.

## 1) Требования к окружению

- Python **3.14+**
- `pip`
- (опционально) `venv`
- Docker 24+ и Docker Compose v2 (если запускать контейнером)

## 2) Подготовка проекта

1. Перейдите в корень репозитория.
2. Убедитесь, что файл `.cm-token` существует и содержит **только ваш токен** в одной строке.

Пример создания файла:

```bash
echo "<ВАШ_CM_TOKEN>" > .cm-token
```

## 3) Локальный запуск (без Docker)

### 3.1 Создание и активация виртуального окружения

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

### 3.2 Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Запуск сервера

```bash
python -m src.main
```

Сервер стартует на:

- `0.0.0.0:8000`

## 4) Проверка работоспособности API

### 4.1 Проверка эндпоинта задачи 1

```bash
curl -X POST http://127.0.0.1:8000/api/v1/robinson_cruise \
  -H "Content-Type: application/json" \
  -d '{"shuttle_coordinates":[0,0],"robinson_coordinates":[1,1],"drifting_speed":1,"time_limit":10,"black_holes":[]}'
```

### 4.2 Проверка эндпоинта задачи 2

```bash
curl -X POST http://127.0.0.1:8000/api/v1/star_visibility \
  -H "Content-Type: application/json" \
  -d '{"observation_params":{"required_transmission_time":1},"celestial_bodies":[],"target_star_vector":[1,0,0]}'
```

### 4.3 Проверка эндпоинта задачи 3

```bash
curl -X POST http://127.0.0.1:8000/api/v1/constellation_finder \
  -H "Content-Type: application/json" \
  -d '{"observation_dates":[{"date":"2026-01-01","stars":[[0,0],[1,1],[2,2]]}],"constellation":[[0,1],[1,2]]}'
```

## 5) Сборка и запуск через Docker

### 5.1 Сборка образа

```bash
docker build -t space-rescue-api:local .
```

### 5.2 Запуск контейнера

```bash
docker run --rm -p 8000:8000 space-rescue-api:local
```

После запуска API доступно по адресу `http://127.0.0.1:8000`.

## 6) Публикация и запуск через docker-compose

1. Соберите образ и запушьте его в GitVerse Registry.
2. Обновите в `docker-compose.yml` значение `image` на ваш опубликованный образ.
3. Запустите:

```bash
docker compose up -d
```

4. Проверка:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/robinson_cruise -H "Content-Type: application/json" -d '{}'
```

(ожидается валидный ответ API, включая обработку ошибочного ввода).
