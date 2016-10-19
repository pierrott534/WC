#!/usr/bin/python
import socket, sys

HOST = 'rasp'
PORT = 50000

def retour_sock(sonde):
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
	mySocket.send(sonde)
	val1 = mySocket.recv(1024)
	val2 = mySocket.recv(1024)
	mySocket.send("STOP")
	msgClient =  mySocket.recv(1024)
	if (msgClient == "STOP"):
	        mySocket.close()
	print "Connexion interrompue."
	mySocket.close()
	return(val1 , val2)

temp = retour_sock("IN")
print("%s" % temp[0])
print("%s" % temp[1])
