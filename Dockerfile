FROM ubuntu:22.04
RUN apt-get update && apt-get install -y build-essential git make autotools-dev automake python3 nano patch && \
    mkdir /dependencies

WORKDIR /dependencies
COPY patches/rsbep-safety.patch /dependencies/rsbep-safety.patch

RUN git clone --branch v0.2.0 --depth 1 https://github.com/ttsiodras/rsbep-backup.git && \
    patch -p1 < rsbep-safety.patch && \
    cd rsbep-backup && \
    ./configure && \
    make && \
    make install

COPY scripts /scripts
WORKDIR /scripts
ENTRYPOINT ["/bin/bash"]