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


SEUIL = '20'
FILE = '/var/www/WC/realtime.txt'
FILE2 = '/var/www/WC/realtime.xml'
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
#	print "Connexion etablie avec le serveur."

	# 3) Dialogue avec le serveur :
	msgServeur = mySocket.recv(1024)
	mySocket.send(sonde)
	val1 = mySocket.recv(1024)
	val2 = mySocket.recv(1024)
	mySocket.send("STOP")
	msgClient =  mySocket.recv(1024)
	if (msgClient == "STOP"):
	        mySocket.close()
#	print "Connexion interrompue."
	mySocket.close()
	return(val1 , val2)

def sendTextMail(text):
	fromaddr = "METEO <meteo@free.fr>"
	liste_destinataires=['maison.tirole@free.fr']
    	mail = MIMEText(text)
    	mail['From'] = fromaddr
    	mail['Subject'] = "Alerte Temperature"
    	smtp = smtplib.SMTP()
    	smtp.connect()
    	for d in liste_destinataires:
    		smtp.sendmail(fromaddr,d,mail.as_string())
    	smtp.close()

def envoi_mail(temp):
	corps = """\
Bonjour,
 
La temperature mesuree est inferieure a %s degres.
Elle est de %s
 
""" % (SEUIL,temp)
	corps+="""\
"""
 
	sendTextMail(corps)


# Read sensors (indoor/outdoor temperature + humidity) :
indoor_results = retour_sock("IN")
pression = retour_sock("PR")
pressure = pression[0]
tempss = pression[1]
outdoor_results = retour_sock("EX")

indoor_temp = indoor_results[0]
indoor_humidity = indoor_results[1]
outdoor_temp = outdoor_results[0]
outdoor_humidity = outdoor_results[1]
contenu = ["vide" , "vide"]

file = open(FILE, "r")
contenu = file.read()
file.close()
contenu = contenu.split(" ")
longueur = len(contenu)
rajout = 58 - longueur

for i in range(rajout):
  contenu.append(i)

Heure = float(time.strftime('%H',time.localtime()))

if (Heure == 0):
   contenu[26] = outdoor_temp
   contenu[27] = time.strftime('%H:%M',time.localtime())
   contenu[28] = outdoor_temp
   contenu[29] = time.strftime('%H:%M',time.localtime())
   contenu[34] = pressure
   contenu[35] = time.strftime('%H:%M',time.localtime())
   contenu[36] = pressure
   contenu[37] = time.strftime('%H:%M',time.localtime())
else:
  if (float(contenu[26]) < float(outdoor_temp)):
      contenu[26] = outdoor_temp
      contenu[27] = time.strftime('%H:%M',time.localtime())
  if (float(contenu[28]) > float(outdoor_temp)):
      contenu[28] = outdoor_temp
      contenu[29] = time.strftime('%H:%M',time.localtime())
  if (float(contenu[34]) > pressure):
      contenu[34] =pressure
      contenu[35] = time.strftime('%H:%M',time.localtime())
  if (float(contenu[36]) < pressure):
      contenu[36] = pressure
      contenu[37] = time.strftime('%H:%M',time.localtime())



contenu[0] = time.strftime('%d/%m/%y',time.localtime())
contenu[1] = time.strftime('%H:%M:%S',time.localtime())
if (float(outdoor_temp) > float(contenu[2])):
   contenu[25] = "+%.2f" % (float(outdoor_temp) - float(contenu[2]))
else:
   contenu[25] = "%.2f" % (float(outdoor_temp) - float(contenu[2]))
contenu[2] = outdoor_temp
contenu[3] = outdoor_humidity
contenu[4] = "NA"
contenu[5] = "NA"
contenu[6] = "NA"
contenu[7] = "NA"
contenu[8] = "NA"
contenu[9] = "NA"
if (pressure > float(contenu[10])):
  contenu[18] = "+%.2f" % (float(pressure) - float(contenu[10]))
else:
  contenu[18] = "%.2f" % (float(pressure) - float(contenu[10]))
contenu[10] = pressure
contenu[11] = "NA"
contenu[12] = "NA"
contenu[13] = "km/h"
contenu[14] = "C"
contenu[15] = "hPa"
contenu[16] = "mm"
contenu[17] = "NA"
contenu[19] = "NA"
contenu[20] = "NA"
contenu[21] = "NA"
contenu[22] = indoor_temp
contenu[23] = indoor_humidity
contenu[24] = "NA"
contenu[30] = "NA"
contenu[31] = "NA"
contenu[32] = "NA"
contenu[33] = "NA"
contenu[38] = "NA"
contenu[39] = "NA"
contenu[40] = "NA"
contenu[41] = "NA"
contenu[42] = "NA"
contenu[43] = "NA"
contenu[44] = "NA"
contenu[45] = "NA"
contenu[46] = "NA"
contenu[47] = "NA"
contenu[48] = "NA"
contenu[49] = "NA"
contenu[50] = "NA"
contenu[51] = "NA"
contenu[52] = "NA"
contenu[53] = "NA"
contenu[54] = "NA"
contenu[55] = tempss
contenu[56] = "NA"
contenu[57] = "NA"

#file = open(FILE, "w")
#for element in contenu:
#  file.write(element)
#  file.write(" ")
#file.close()

BASE =  "http://maisontirole.3utilities.com/emoncms/input/post.json?node1&csv=%s,%s,%s&apikey=79db7b521aec410afc918a92bee06ccd" % (contenu[2], contenu[3], contenu[10])
#urllib2.urlopen(BASE)

SMS = "/usr/local/bin/googalert \"Temperature en alerte de %s\" \"Temperature interieure de %s\" " % (contenu[22], contenu[22])

if (float(indoor_temp) < float (SEUIL)):
   envoi_mail(indoor_temp)
   os.system("%s" % SMS)
 
file = open(FILE2, "w")
file.write("<?xml version=\"1.0\" encoding=\"ISO-8859-15\" ?>\n")
file.write("<maintag>\n")
file.write("<misc>\n")
file.write("<data misc=\"refresh_time\">%s 20:01:34</data>\n" % contenu[0])
file.write("</misc>\n")
file.write("<misc>\n")
file.write("<data misc=\"forecast_nr\">9</data>\n")
file.write("</misc>\n")
file.write("<realtime>\n")
file.write("<data misc=\"winddir\">N</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data misc=\"location\">Bourgoin-Jallieu</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"forecast_text\">Showery early, improving</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"temp\">%s C</data>\n" % outdoor_temp)
file.write("</realtime>\n")
file.write("<realtime>")
file.write("<data realtime=\"intemp\">%s C</data>" % indoor_temp)
file.write("</realtime>")
file.write("<realtime>")
file.write("<data realtime=\"hum\">%s </data>" % outdoor_humidity)
file.write("</realtime>")
file.write("<realtime>")
file.write("<data realtime=\"inhum\">%s </data>" % indoor_humidity)
file.write("</realtime>")
file.write("<realtime>")
file.write("<data realtime=\"press\">%s hPa</data>" % pressure)
file.write("</realtime>")

file.write("</maintag>\n")
file.close()
