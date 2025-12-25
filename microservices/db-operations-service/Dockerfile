FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /base-microservice

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /base-microservice/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /base-microservice/

RUN mkdir -p /base-microservice/exported_tables && chmod 777 /base-microservice/exported_tables


COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8002", "--workers", "2"]