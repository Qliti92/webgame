FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    postgresql-client \
    libpq-dev \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY backend/ /app/
COPY frontend/ /app/frontend/

RUN mkdir -p /app/staticfiles /app/media
