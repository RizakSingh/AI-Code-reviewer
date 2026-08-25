#!/bin/sh
celery -A app.celery_app.celery_app worker --loglevel=info &
exec uvicorn app.main:app --host 0.0.0.0 --port 8000