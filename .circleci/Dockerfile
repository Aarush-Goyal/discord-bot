FROM python:3.8-alpine3.13

RUN apk update && apk upgrade && apk add --no-cache build-base && rm -rf /var/cache/apk/*

RUN pip3 install -U pip wheel setuptools black isort flake8 flake8-black
