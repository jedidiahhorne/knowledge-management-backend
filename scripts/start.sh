#!/bin/bash
# Startup script that runs database migrations before starting the application

# Don't exit on error for migration check, but do exit if DATABASE_URL is missing
set +e

echo "=========================================="
echo "Starting Knowledge Management Backend"
echo "=========================================="

# Check if DATABASE_URL is set (this should exit on error)
set -e
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set!"
    exit 1
fi
set +e

echo "DATABASE_URL is set (length: ${#DATABASE_URL} characters)"

# Run migrations with error handling
echo "Running database migrations..."
if alembic upgrade head; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Migration failed! Check logs above for details."
    echo "Attempting to continue anyway..."
fi

# Show current migration status
echo "Current migration status:"
alembic current || echo "Could not determine migration status"

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

