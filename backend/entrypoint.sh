#!/bin/sh
alembic revision --autogenerate -m "init"
alembic upgrade head
python app/seed.py
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
