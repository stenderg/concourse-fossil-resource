FROM python:3-alpine

RUN apk update && \
    apk add openssh

RUN pip3 install requests && \
    rm -r /root/.cache

COPY src/* /opt/resource/
