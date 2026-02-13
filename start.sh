#!/bin/bash

# Start script for production deployment
# Starts both Gunicorn (API) and Huey (worker)

set -e  # Exit on error

echo "Starting Reel Intelligence Backend..."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start Huey worker in background
echo "Starting Huey worker..."
huey_consumer app.tasks.huey_config.huey \
    --workers $HUEY_WORKERS \
    --worker-type process \
    --logfile huey.log &

# Start Gunicorn with Uvicorn workers
echo "Starting Gunicorn..."
gunicorn app.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-5000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

---

## Procfile (for Railway)
```
web: bash start.sh