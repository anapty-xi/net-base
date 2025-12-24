FROM python:latest

WORKDIR /base-gate

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "congig.wsgi:application", "-b", "127.0.0.1:8000", "--workers", "2"]