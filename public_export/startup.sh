#!/bin/bash
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH:.
cd /home/site/wwwroot
gunicorn --bind=[PRIVATE_IP]:8000 --workers=2 --timeout=600 app:app
