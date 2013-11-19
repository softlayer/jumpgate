#!/bin/sh
gunicorn jumpgate.api:api -c testing.cfg
