FROM python:3.8

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR /code

COPY /requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . ./

CMD exec gunicorn --bind :$PORT --workers 1 --threads 1 --timeout 3600 main:app