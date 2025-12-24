FROM python:latest

ENV PYTHONDONTWRITEBITECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /base-microservice

COPY requirements.txt /base-microservice/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "congig.wsgi:application", "-b", "127.0.0.1:8001", "--workers", "2"]