FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

ARG DJANGO_ENV=development
ENV DJANGO_ENV=$DJANGO_ENV

CMD if [ "$DJANGO_ENV" = "production" ]; then \
        gunicorn myapp.wsgi:application --bind 0.0.0.0:8000; \
    else \
        python manage.py runserver 0.0.0.0:8000; \
    fi
