FROM python:3.12-slim

WORKDIR /app

# 必要なビルドツールとヘッダーをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir  -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD /bin/sh -c 'if [ "$DJANGO_ENV" = "production" ]; then \
                    uwsgi --ini uwsgi.ini; \
                else \
                    python manage.py runserver_plus 0.0.0.0:8000; \
                fi'



