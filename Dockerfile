FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD if [ "$DJANGO_ENV" = "production" ]; then \
        gunicorn config.wsgi:application --bind 0.0.0.0:8000; \
    else \
        python manage.py runserver_plus 0.0.0.0:8000; \
    fi
