FROM python:3.8-alpine3.13

WORKDIR /home/app

RUN apk update && apk upgrade && \
    apk add --no-cache bash git build-base && \
    rm -rf /var/cache/apk/*

RUN pip3 install -qU pip wheel setuptools
COPY ./requirements.txt .
RUN pip3 install -qr requirements.txt
COPY ./ .

CMD ["python", "main.py"]
