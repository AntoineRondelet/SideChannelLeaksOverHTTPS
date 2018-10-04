FROM python:2.7-jessie

RUN apt-get update && apt-get install -y \
    net-tools \
    curl \
    tcpdump \
    wget \
    dnsutils \
    vim \
    sudo
    # tshark

COPY . /home/src

RUN pip install -r /home/src/requirements.txt

# Change the password for the root user
RUN echo "xxx" | passwd --stdin root

WORKDIR /home/src

CMD ["/bin/bash"]
