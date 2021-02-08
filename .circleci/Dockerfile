FROM python:3.7-alpine3.12

RUN  apk update && apk upgrade && apk add --no-cache build-base && rm -rf /var/cache/apk/*

RUN pip3 install -U pip wheel setuptools black isort
