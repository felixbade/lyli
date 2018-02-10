FROM python:alpine
ADD . /code
WORKDIR /code
RUN apk update && apk add build-base ca-certificates curl libffi-dev musl openssl openssl-dev zlib-dev
RUN pip install -r requirements.txt
