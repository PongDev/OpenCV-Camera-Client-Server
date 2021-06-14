FROM debian:latest

RUN apt update && apt upgrade -y && apt install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    python3-opencv

COPY ./.env /home/VideoServer/.env
COPY ./requirements.txt /home/VideoServer/requirements.txt
COPY ./server.py /home/VideoServer/server.py
COPY ./server.wsgi /home/VideoServer/server.wsgi
COPY ./server.conf /etc/apache2/sites-available/server.conf

RUN pip3 install --upgrade pip
RUN pip3 install -r /home/VideoServer/requirements.txt

RUN a2dissite 000-default
RUN a2ensite server

RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log

EXPOSE ${SERVER_PORT}
EXPOSE 80

CMD /usr/sbin/apache2ctl -D FOREGROUND
