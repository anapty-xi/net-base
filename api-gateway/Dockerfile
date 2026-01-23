FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /gate

COPY requirements.txt /gate/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /gate/

HEALTHCHECK --interval=90s --timeout=5s --start-period=20s --start-interval=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://127.0.0.1:8000/health/').raise_for_status()" || exit 1

CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "2"]