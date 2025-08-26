#!/bin/sh
# wait-for-it.sh
until curl -s http://django.service.local:8000/health/; do
  echo "Waiting for Django..."
  sleep 2
done

exec nginx -g 'daemon off;'
