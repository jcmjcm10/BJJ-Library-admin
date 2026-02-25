FROM ubuntu:24.04  

# Instalamos python y dependencias necesarias                                                                                                                                                                                        
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip

RUN ln -s /usr/bin/python3.12 /usr/bin/python

WORKDIR /app

ADD ./requirements.txt /app

RUN python3.12 -m pip install --break-system-packages -r requirements.txt