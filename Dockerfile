# Используем официальный легкий образ Python
FROM python:3.14-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Предотвращаем создание файлов .pyc и включаем логирование в реальном времени
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта (включая папку src и .cm-token)
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Запускаем приложение. 
# Используем конструкцию модуля, чтобы импорты внутри src работали корректно.
CMD ["python", "-m", "src.main"]
