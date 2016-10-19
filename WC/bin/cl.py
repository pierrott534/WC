#!/usr/bin/python
import socket, sys

HOST = 'rasp'
PORT = 50000

# 1) creation du socket :
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2) envoi d'une requete de connexion au serveur :
try:
    mySocket.connect((HOST, PORT))
except socket.error:
    print "La connexion a echouee"
    sys.exit()
print "Connexion etablie avec le serveur."

# 3) Dialogue avec le serveur :
msgServeur = mySocket.recv(1024)
mySocket.send("IN")
ITemp = mySocket.recv(1024)
IHum = mySocket.recv(1024)
mySocket.send("EX")
ETemp = mySocket.recv(1024)
EHum = mySocket.recv(1024)
mySocket.send("PR")
Pres = mySocket.recv(1024)
Temp = mySocket.recv(1024)
print ("Temp Int %s" % ITemp)
print ("Hum Int %s" % IHum)
print ("Temp Ext %s" % ETemp)
print ("Hum Ext %s" % EHum)
print ("Pression %s" % Pres)
print ("Temp %s" % Temp)
mySocket.send("STOP")
msgClient =  mySocket.recv(1024)
if (msgClient == "STOP"):
        mySocket.close()
# 4) Fermeture de la connexion :
print "Connexion interrompue."
mySocket.close()
