FROM python:3.7-slim

ARG APP_USER=feeder
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential libpq-dev \
    && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove gcc build-essential libpq-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

USER ${APP_USER}:${APP_USER}