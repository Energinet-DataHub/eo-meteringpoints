#!/bin/bash
gunicorn 'measurements_api.app:create_app()' -w 2 --threads 2 -b 0.0.0.0:80
