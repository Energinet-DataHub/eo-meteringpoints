#!/bin/sh

if ! docker info > /dev/null 2>&1; then
  echo "This script uses docker, and it isn't running - please start docker and try again"
  exit 1
fi

export PYTHONPATH=$(pwd)/src
pytest tests/integrationstest