FROM python:3.6-alpine3.8
MAINTAINER Keith Moss <keithamoss@gmail.com>

ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV /env
ENV PYTHON_PIP_VERSION 9.0.1

RUN pyvenv "$VIRTUAL_ENV" && \
  "$VIRTUAL_ENV"/bin/pip install -U pip==$PYTHON_PIP_VERSION

ENV PATH "$VIRTUAL_ENV"/bin:$PATH

RUN mkdir /app

WORKDIR /app

RUN apk update
RUN apk add --virtual .build-deps gcc musl-dev libxml2-dev libxslt-dev && rm -rf /var/cache/apk/*

ADD requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir
ADD . /app/
RUN apk --purge del .build-deps gcc musl-dev libxml2-dev libxslt-dev

WORKDIR /app/api

ENTRYPOINT ["/app/docker-entrypoint.sh"]
