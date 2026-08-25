#!/bin/sh
echo "Running database migrations..."
alembic upgrade head

echo "Starting celery worker..."
celery -A app.celery_app.celery_app worker --loglevel=info --pool=solo --concurrency=1 &

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000