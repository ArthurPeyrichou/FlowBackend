# FlowBackend

Prérequis
=============

Installez les modules python nécessaires :

`pip install websockets`
`pip install pycryptodome`

Générez une clef privé, renommez la ssl-key.pem et mettez la dans le dossier keys/.

Générez une clef de certificat ssl, renommez la https-cert.pem et mettez la dans le dossier keys/.

Générez un couple clef privée/public de taille 2048, renommez les rsa_2048_priv.pem, rsa_2048_pub.pem et mettez les dans le dossier keys/.


Pour générer les clefs nécessaires depuis la racine du projet:

openssl genrsa -out keys/rsa_2048_priv.pem 2048 && openssl rsa -pubout -in keys/rsa_2048_priv.pem -out keys/rsa_2048_pub.pem

openssl genrsa -out keys/ssl-key.pem 4096 && openssl req -new -x509 -key keys/ssl-key.pem -out keys/ssl-cert.pem -days 1095


Configuration
=============

Pour démarrer le serveur websocket, taper :

`py server.py`

> Le serveur tourne sur le port 8765 par default (https://localhost:8765)

Si vous utilisez un certificat ssl que vous avez créé vous-même; vous devez utiliser un navigateur, vous rendre sur l'adresse ci-dessus, et clicker sur "Détails" puis sur "Accepter les risques" pour pouvoir communiquer par la suite.