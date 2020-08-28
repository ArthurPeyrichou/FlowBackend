Backend, operating around parallelized autonomous cores that will be built by
operators who are experts in their fields.
=============================================================

PEYRICHOU Arthur

Prerequisite
=============

Install the necessary python modules (they are in requirements.txt file)

Generate a private key, rename it ssl-key.pem and put it in the keys/ folder.

Generate an ssl certificate key, rename it https-cert.pem and put it in the keys/ folder.

Generate a private/ public key pair of size 2048, rename them "rsa_2048_priv.pem" and "rsa_2048_pub.pem", then put them in the keys/ folder.


To generate the necessary keys from the root of the project:

openssl genrsa -out keys/rsa_2048_priv.pem 2048 && openssl rsa -pubout -in keys/rsa_2048_priv.pem -out keys/rsa_2048_pub.pem

openssl genrsa -out keys/ssl-key.pem 4096 && openssl req -new -x509 -key keys/ssl-key.pem -out keys/ssl-cert.pem -days 1095


Configurations
=============

Pour démarrer le serveur websocket, taper :

`py server.py`

> The server is running on port 5001 by default (https://localhost:5001)

If you are using an ssl certificate that you created yourself; you must use a browser, go to the address above, it will stop you with an warning. Click on "Details" then on "Accept the risks" to be able to communicate thereafter.

Docker
=============

To start the server vue.JS with docker, go to the root folder and type :

`docker build -t dataflow:backend .`
`docker run -it -p 5001:5001 --rm --name dataflow:backend-1 dataflow:backend`
