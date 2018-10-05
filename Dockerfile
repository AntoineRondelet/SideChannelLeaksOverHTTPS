FROM python:2.7-alpine

RUN apk update && apk add --no-cache \
    net-tools \
    tcpdump \
    wget \
    vim \
    libxml2 \
    libxslt \
    sudo \
    tshark

RUN apk add --update --no-cache g++ gcc libxslt-dev

COPY . /home/src

RUN pip install -r /home/src/requirements.txt

WORKDIR /home/src

CMD ["/bin/sh"]
