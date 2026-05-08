#!/bin/bash
set -e

# Wait for database
echo "Waiting for database..."
while ! nc -z ${DB_HOST:-localhost} ${DB_PORT:-5432}; do
  sleep 1
done
echo "Database ready"

# Run migrations (if using Alembic)
alembic upgrade head

# Start application
exec "$@"