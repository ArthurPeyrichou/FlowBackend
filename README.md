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

- `openssl genrsa -out keys/rsa_4096_priv.pem 4096 && openssl rsa -pubout -in keys/rsa_4096_priv.pem -out keys/rsa_4096_pub.pem`

- `openssl genrsa -out keys/ssl-key.pem 4096 && openssl req -new -x509 -key keys/ssl-key.pem -out keys/ssl-cert.pem -days 365 -subj '/CN=localhost'`


Configurations
=============

To start websocket server, type :

- `py server.py`

> The server is running on port 5001 by default (wss://localhost:5001)

Docker
=============

To start the server vue.JS with docker, go to the root folder and type :

Don't forget to install first components in components/ folder if needed.
Link: https://github.com/Rarioty/DataFlow-Components.git

- `docker build -t dataflow:backend .`
- `docker run -it -p 5001:5001 --rm --name dataflow-backend-1 dataflow:backend`

Caution
=============

If you are using a ssl certificate that you created automatically, you must use a browser, go to the address above (https://localhost:5001), it will stop you with a warning. Click on "Details" then on "Accept the risks" to be able to communicate thereafter. Then it will tail you that the connection can't be done because you request a https connection and it is a websocket communication but the ssh certificat is now accepted and the frontend can communicate with the backend.

Thanks
=============

This work is based on the prototype app from Arthur Chevalier (https://github.com/Rarioty)

