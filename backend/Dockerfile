FROM python:3.12-alpine

LABEL maintainer="Saez24" \
      version="1.0" \
      description="Python 3.14.0a7 Alpine 3.21"

WORKDIR /app

COPY . .

RUN apk update && \
    apk add --no-cache --upgrade bash && \
    apk add --no-cache \
        ffmpeg \
        libffi-dev \
        libpq \
        postgresql-client && \
    apk add --no-cache --virtual .build-deps \
        gcc \
        libffi-dev \
        libpq-dev \
        musl-dev \
        postgresql-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    chmod +x backend.entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./backend.entrypoint.sh"]
