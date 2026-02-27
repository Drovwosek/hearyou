FROM python:3.11-slim

# Установка ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg file && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование всего (build context = hearyou/packages/)
COPY stt-yandex/*.py ./
COPY stt-yandex/corrections.example.json ./

COPY stt-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stt-service/app.py .
COPY stt-service/static/ ./static/

# Создание директорий
RUN mkdir -p uploads results temp logs chunks

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "900"]
