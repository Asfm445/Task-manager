#!/bin/bash
# Exit on error
set -e

echo "Running migrations..."
alembic upgrade head

# Run the container CMD
exec "$@"
