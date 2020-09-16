FROM python:latest

ARG HTTP_PROXY
ARG HTTPS_PROXY

RUN mkdir /app

WORKDIR /app
ADD . /app/

RUN export HTTP_PROXY=$HTTP_PROXY
RUN export HTTPS_PROXY=$HTTPS_PROXY

RUN pip install -r requirements.txt
RUN openssl genrsa -out keys/rsa_4096_priv.pem 4096 && openssl rsa -pubout -in keys/rsa_4096_priv.pem -out keys/rsa_4096_pub.pem
RUN openssl genrsa -out keys/ssl-key.pem 4096 && openssl req -new -x509 -key keys/ssl-key.pem -out keys/ssl-cert.pem -days 365 -subj '/CN=localhost'

EXPOSE 5001

CMD python server.py
