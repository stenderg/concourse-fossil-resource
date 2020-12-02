FROM python:3.6.3-alpine3.6

RUN apk update && \
    apk add openssh

RUN pip3 install requests && \
    rm -r /root/.cache

COPY src/* /opt/resource/