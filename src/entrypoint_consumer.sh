#!/bin/bash
set -e

echo "Starting Message Bus consumer"
cd migrations && alembic upgrade head && cd ..
python -m meteringpoints_consumer
