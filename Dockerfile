FROM ubuntu:22.04
RUN apt update && apt install -y build-essential git make autotools-dev automake python3 nano && \
    mkdir /dependencies

WORKDIR /dependencies

RUN git clone https://github.com/ttsiodras/rsbep-backup.git && \
    cd rsbep-backup && \
    ./configure && \
    make && \
    make install

COPY scripts /scripts
WORKDIR /scripts
ENTRYPOINT ["/bin/bash"]