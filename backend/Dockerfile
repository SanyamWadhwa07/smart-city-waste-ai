FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG INSTALL_YOLO=0

COPY requirements.txt /app/requirements.txt
COPY requirements-yolo.txt /app/requirements-yolo.txt

RUN pip install --no-cache-dir -r /app/requirements.txt \
    && if [ "$INSTALL_YOLO" = "1" ]; then pip install --no-cache-dir -r /app/requirements-yolo.txt; fi

COPY app /app/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
