FROM public.ecr.aws/docker/library/python:3.11-slim

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

# ШАГ 1: Устанавливаем зависимости ПЕРВЫМИ (кешируется!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ШАГ 2: Копируем код (меняется часто, но не инвалидирует кеш requirements)
COPY core/ ./core/
COPY app.py .
COPY static/ ./static/
COPY ispring_hints.py .
COPY speaker_diarization_resemblyzer.py .
COPY speaker_diarization_pyannote.py .
# Используем example-файл как надёжный источник исправлений,
# чтобы сборка не зависела от наличия отдельного JSON в контексте Timeweb.
COPY corrections.example.json ./ispring_corrections.json
COPY corrections.example.json ./core/ispring_corrections.json

# Создание директорий
RUN mkdir -p uploads results temp logs chunks

ENV WHISPER_MODEL=small \
    WHISPER_DEVICE=cpu \
    WHISPER_COMPUTE_TYPE=int8 \
    WHISPER_MODEL_DIR=/app/models

RUN mkdir -p /app/models

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "900"]
