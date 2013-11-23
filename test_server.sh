#!/bin/sh
JUMPGATE_CONFIG=etc/jumpgate.conf gunicorn jumpgate.wsgi:make_api --bind="127.0.0.1:5000" --timeout=600 --access-logfile="-"
