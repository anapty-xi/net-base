FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /base-microservice

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libc6-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /base-microservice/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /base-microservice/

RUN mkdir -p /base-microservice/exported_tables && chmod 777 /base-microservice/exported_tables

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

HEALTHCHECK --interval=90s --timeout=5s --start-period=20s --start-interval=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://127.0.0.1:8002/health/').raise_for_status()" || exit 1

CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8002", "--workers", "2"]