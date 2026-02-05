FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y gcc python3 python3-pip build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

VOLUME [ "/sandbox" ]
WORKDIR /sandbox
# COPY ./test .

RUN useradd -ms /bin/bash sandboxuser && \
    chown -R sandboxuser:sandboxuser /sandbox
USER sandboxuser

CMD [ "bash" ]
