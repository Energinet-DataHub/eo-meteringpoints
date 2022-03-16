#!/bin/bash
set -e

# Run API
gunicorn 'meteringpoints_api.app:create_app()' -w 2 --threads 2 -b 0.0.0.0:80
