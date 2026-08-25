#!/bin/bash
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH:.
cd /home/site/wwwroot
gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout=600 app:app
