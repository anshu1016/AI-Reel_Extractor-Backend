#!/bin/bash
# start.sh

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start Huey consumer in the background
echo "Starting Huey consumer..."
# Reduced to 1 worker to save memory on Render
huey_consumer app.tasks.huey_config.huey --workers 1 &

# Start FastAPI application
echo "Starting FastAPI server..."
# Using 1 worker to keep memory footprint low on small instances
gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT