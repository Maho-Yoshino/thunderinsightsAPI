FROM python:3.12.3-alpine3.18

RUN apk add build-base

RUN apk add mariadb-dev

RUN apk add gcc python3-dev musl-dev linux-headers

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

WORKDIR /code/app

CMD ["celery", "-A", "main", "worker", "--loglevel=info", "-B", "-s", "/code/app/celerybeat-schedule"]