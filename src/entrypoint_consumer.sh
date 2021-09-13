#!/bin/bash
set -e

echo "Starting Message Bus consumer"
cd src/migrations && alembic upgrade head && cd ../..
python -m meteringpoints_consumer
