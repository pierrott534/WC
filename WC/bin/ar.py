#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-

# Thierry Jouve - Bruno Chevillion - 27/06/13
# Addon et Modif P TIROLE

import urllib2
import smtplib
import os
import sys
import subprocess
import re
import time
import socket
from email.MIMEText import MIMEText


HOST = 'rasp'
PORT = 50000
HOST2 = 'rasp'
PORT2 = 50001

def retour_sock(host, port, sonde):
	# 1) creation du socket :
	mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# 2) envoi d'une requete de connexion au serveur :
	try:
	    mySocket.connect((host, port))
	except socket.error:
	    print "La connexion a echouee avec %s sur port %d" % (host, port)
	    sys.exit()
	print "Connexion etablie avec le serveur sur port %d." % port

	# 3) Dialogue avec le serveur :
	msgServeur = mySocket.recv(1024)
	mySocket.send(sonde)
	val1 = mySocket.recv(1024)
	mySocket.send("STOP")
	msgClient =  mySocket.recv(1024)
	if (msgClient == "STOP"):
	        mySocket.close()
#	print "Connexion interrompue."
	mySocket.close()
	return(val1)

# Read sensors (indoor/outdoor temperature + humidity) :
ligne = retour_sock(HOST, PORT2, "AR")
print ligne
