FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /base-microservice

COPY requirements.txt /base-microservice/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /base-microservice/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8001", "--workers", "2"]