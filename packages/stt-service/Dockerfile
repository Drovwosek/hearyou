FROM python:3.11-slim

# Установка системных зависимостей и build tools
RUN apt-get update && \
    apt-get install -y \
        ffmpeg \
        file \
        build-essential \
        gcc \
        g++ && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование core модулей (build context = hearyou/)
COPY core/ ./core/
COPY packages/stt-service/.env.yandex ./core/.env.yandex

# Копирование stt-service файлов
COPY packages/stt-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY packages/stt-service/app.py .
COPY packages/stt-service/static/ ./static/
COPY packages/stt-service/ispring_hints.py .
COPY packages/stt-service/speaker_diarization_resemblyzer.py .
COPY packages/stt-service/ispring_corrections.json .

# Создание директорий
RUN mkdir -p uploads results temp logs chunks

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "900"]
