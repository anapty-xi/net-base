FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /gate

COPY requirements.txt /gate/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /gate/

CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "2"]