FROM debian:latest

RUN apt update && apt upgrade -y && apt install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    python3-opencv \
    ninja-build \
    cmake \
    libssl-dev \
    screen

COPY ./.env /home/VideoServer/.env
COPY ./CameraServer.py /home/VideoServer/CameraServer.py
COPY ./requirements.txt /home/VideoServer/requirements.txt
COPY ./VideoStream.conf /etc/apache2/sites-available/VideoStream.conf
COPY ./VideoStream.py /home/VideoServer/VideoStream.py
COPY ./VideoStream.wsgi /home/VideoServer/VideoStream.wsgi

RUN pip3 install --upgrade pip
RUN pip3 install -r /home/VideoServer/requirements.txt

RUN a2dissite 000-default
RUN a2ensite VideoStream

RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log

EXPOSE ${SERVER_PORT}
EXPOSE 80

CMD screen -dmS CameraServer /usr/bin/python3 /home/VideoServer/CameraServer.py && /usr/sbin/apache2ctl -D FOREGROUND
