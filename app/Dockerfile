# pull official base image
FROM python:3.8-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# install psycopg2
RUN pip install --upgrade pip \
    && apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

# copy project
COPY . .

## install dependencies
RUN pip install -r requirements/production.txt

# run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

# add and run as non-root user
RUN adduser -D michal
RUN chown michal:michal -R /app
USER michal


