FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FASTAPI_PORT=8000

WORKDIR /app

COPY backend-query/requirements/requirements.txt /requirements/requirements.txt

RUN pip install --no-cache-dir -r /requirements/requirements.txt

COPY backend-query/. /app/

CMD fastapi run src/main.py --port $FASTAPI_PORT
