FROM python:3.10.0a4-alpine3.12
RUN apk update && apk upgrade && \
    apk add --no-cache bash git
RUN apk add build-base
RUN mkdir /home/app
WORKDIR /home/app
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY ./ .
CMD ["python","main.py"]
