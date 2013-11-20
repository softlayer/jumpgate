#!/bin/sh
gunicorn jumpgate.wsgi:api --bind="127.0.0.1:5000" --timeout=600 --access-logfile="-"
