#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-

# Thierry Jouve - Bruno Chevillion - 27/06/13
# Addon et Modif P TIROLE
from __future__ import with_statement

import urllib2
import smtplib
import os
import sys
import subprocess
import re
import time
import socket
import contextlib
from email.MIMEText import MIMEText


SEUIL = '19'
FILE = '/var/www/html/WC/realtime.txt'
FILE2 = '/var/www/html/WC/realtime.xml'
HOST = 'rasp'
PORT = 50000
PORT2 = 50001

TAB = [ 'winddir','windspeedkmh','windgustkmh','windgustdir','windspdkmh_avg2m','winddir_avg2m','windgustkmh_10m','windgustdir_10m','humidity','temp','pressure','rainmm','dailyrainmm','light_lvl']
TABfr = [ 'Direction du vent','Vitesse du vent','Vitesse des rafales de vent','Direction des rafales de vent','windspdkmh_avg2m','winddir_avg2m','windgustkmh_10m','windgustdir_10m','Humidite','Temperature','Pression','Pluie','Pluie sur la journee','light_lvl']


def _(msg) : return msg

forecast_text = {
    'A' : _("1"),
    'B' : _("2"),
    'C' : _("3"),
    'D' : _("4"),
    'E' : _("5"),
    'F' : _("6"),
    'G' : _("7"),
    'H' : _("8"),
    'I' : _("9"),
    'J' : _("10"),
    'K' : _("11"),
    'L' : _("12"),
    'M' : _("13"),
    'N' : _("14"),
    'O' : _("15"),
    'P' : _("16"),
    'Q' : _("17"),
    'R' : _("18"),
    'S' : _("19"),
    'T' : _("20"),
    'U' : _("21"),
    'V' : _("22"),
    'W' : _("23"),
    'X' : _("24"),
    'Y' : _("25"),
    'Z' : _("26")
    }

del _

def VENT(lang, wind):
	windstr="Err"
	if wind == 0 or wind == "0":
	  windstr="N"
	elif wind == 23 or wind == "23":
#	  if lang == "FR":
	    windstr="NNE"
#	  else:
#	    windstr="NNW"
	elif wind == 45 or wind == "45":
#	  if lang == "FR":
	    windstr="NE"
#	  else:
#	    windstr="NW"
	elif wind == 68 or wind == "68":
#	  if lang == "FR":
	    windstr="ENE"
#	  else:
#	    windstr="WNW"
	elif wind == 90 or wind == "90":
#	  if lang == "FR":
	    windstr="E"
#	  else:
#	    windstr="W"
	elif wind == 113 or wind == "0":
#	  if lang == "FR":
	    windstr="ESE"
#	  else:
#	    windstr="WSW"
	elif wind == 135 or wind == "135":
#	  if lang == "FR":
	    windstr="SE"
#	  else:
#	    windstr="SW"
	elif wind == 158 or wind == "158":
#	  if lang == "FR":
	    windstr="SSE"
#	  else:
#	    windstr="SSW"
	elif wind == 180 or wind == "180":
	  windstr="S"
	elif wind == 203 or wind == "203":
	  if lang == "FR":
	    windstr="SSO"
	  else:
	    windstr="SSW"
	elif wind == 225 or wind == "225":
	  if lang == "FR":
	    windstr="SO"
	  else:
	    windstr="SW"
	elif wind == 248 or wind == "248":
	  if lang == "FR":
	    windstr="OSO"
	  else:
	    windstr="WSW"
	elif wind == 270 or wind == "270":
	  if lang == "FR":
	    windstr="O"
	  else:
	    windstr="W"
	elif wind == 293 or wind == "293":
	  if lang == "FR":
	    windstr="ONO"
	  else:
	    windstr="WNW"
	elif wind == 315 or wind == "315":
	  if lang == "FR":
	    windstr="NO"
	  else:
	    windstr="NW"
	elif wind == 338 or wind == "338":
	  if lang == "FR":
	    windstr="NNO"
	  else:
	    windstr="NNW"
	else:
	  windstr="Err"
	return windstr

def ZambrettiCode(pressure, month, wind, trend,
                  north=True, baro_top=1050.0, baro_bottom=950.0):
    """Simple implementation of Zambretti forecaster algorithm.
    Inspired by beteljuice.com Java algorithm, as converted to Python by
    honeysucklecottage.me.uk, and further information
    from http://www.meteormetrics.com/zambretti.htm"""
    # normalise pressure
    pressure = 950.0 + ((1050.0 - 950.0) *
                        (pressure - baro_bottom) / (baro_top - baro_bottom))
    # adjust pressure for wind direction
    if wind != None:
        if not north:
            # southern hemisphere, so add 180 degrees
            wind = (wind + 8) % 16
        pressure += (  5.2,  4.2,  3.2,  1.05, -1.1, -3.15, -5.2, -8.35,
                     -11.5, -9.4, -7.3, -5.25, -3.2, -1.15,  0.9,  3.05)[wind]
    # compute base forecast from pressure and trend (hPa / hour)
    if trend >= 0.1:
        # rising pressure
        if north == (month >= 4 and month <= 9):
            pressure += 3.2
        F = 0.1740 * (1031.40 - pressure)
        LUT = ('A', 'B', 'B', 'C', 'F', 'G', 'I', 'J', 'L', 'M', 'M', 'Q', 'T',
               'Y')
    elif trend <= -0.1:
        # falling pressure
        if north == (month >= 4 and month <= 9):
            pressure -= 3.2
        F = 0.1553 * (1029.95 - pressure)
        LUT = ('B', 'D', 'H', 'O', 'R', 'U', 'V', 'X', 'X', 'Z')
    else:
        # steady
        F = 0.2314 * (1030.81 - pressure)
        LUT = ('A', 'B', 'B', 'B', 'E', 'K', 'N', 'N', 'P', 'P', 'S', 'W', 'W',
               'X', 'X', 'X', 'Z')
    # clip to range of lookup table
    F = min(max(int(F + 0.5), 0), len(LUT) - 1)
    # convert to letter code
    return LUT[F]

def ZambrettiText(letter):
    return forecast_text[letter]

def angle(val):
	if int(val) < 270:
		val = int(val)+90
	else:
		val = int(val)-270
	return(val)

def valeur_arduino(ligne):
	text = ligne.split(",")
	nb = 0
	valeur = [0]
	if '$' in text[0]:
	  while nb < 14:
	    if TAB[nb] in text[nb+1]:
		val = text[nb+1].split("=")
		if nb == 0:
		  valeur = [ val[1] ]
		else:
		  valeur.append(val[1])
		nb=nb+1
	return(valeur)

def size():
  with contextlib.closing(open('/etc/mtab')) as fp:
    for m in fp:
      fs_spec, fs_file, fs_vfstype, fs_mntops, fs_freq, fs_passno = m.split()
      if fs_spec.startswith('/'):
        r = os.statvfs(fs_file)
        block_usage_pct = int(100.0 - (float(r.f_bavail) / float(r.f_blocks) * 100))
        return(block_usage_pct)

def retour_sock(host, port, sonde):
	# 1) creation du socket :
	mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# 2) envoi d'une requete de connexion au serveur :
	try:
	    mySocket.connect((host, port))
	except socket.error:
	    print "La connexion %s a echouee avec %s sur port %s" % (sonde,host,port)
	    sys.exit()
	print "Connexion %s etablie avec le serveur." % sonde

	# 3) Dialogue avec le serveur :
	msgServeur = mySocket.recv(1024)
	mySocket.send(sonde)
	val1 = mySocket.recv(1024)
	if (sonde != "AR"):
		val2 = mySocket.recv(1024)
	mySocket.send("STOP")
	msgClient =  mySocket.recv(1024)
	if (msgClient == "STOP"):
	        mySocket.close()
#	print "Connexion interrompue."
	mySocket.close()
	if (sonde == "AR"):
		return(val1)
	else:
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
 
La temperature mesuree par ubuntu est inferieure a %s degres.
Elle est de %s
 
""" % (SEUIL,temp)
	corps+="""\
"""
 
	sendTextMail(corps)


# Read sensors (indoor/outdoor temperature + humidity) :
#indoor_results = retour_sock(HOST, PORT, "IN")
indoor_results = [ 20 , 40 ]
pression = retour_sock(HOST, PORT, "PR")
pressure = pression[0]
tempss = pression[1]
#outdoor_results = retour_sock(HOST, PORT, "EX")

indoor_results[1] = tempss
outdoor_results = [ 15 , 50 ]
ligne = retour_sock(HOST, PORT2, "AR")
arduino=valeur_arduino(ligne)
arduino[0] = angle(arduino[0])
arduino[3] = angle(arduino[3])
arduino[5] = angle(arduino[5])
arduino[7] = angle(arduino[7])

indoor_temp = indoor_results[0]
indoor_humidity = indoor_results[1]
outdoor_temp = arduino[9]
outdoor_humidity = arduino[8]
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
contenu[5] = arduino[1]
contenu[6] = arduino[6]
contenu[7] = VENT("EN",arduino[0])
contenu[8] = arduino[11]
contenu[9] = arduino[12]
#if (pressure > float(contenu[10])):
#  contenu[18] = "+%.2f" % (float(pressure) - float(contenu[10]))
#else:
#  contenu[18] = "%.2f" % (float(pressure) - float(contenu[10]))
contenu[18] = "%.2f" % (float(pressure) - float(contenu[10]))
contenu[10] = pressure
contenu[11] = VENT("EN",arduino[3])
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
contenu[32] = "NA32"
contenu[33] = "NA33"
contenu[38] = "NA38"
contenu[39] = "NA39"
contenu[40] = "NA40"
contenu[41] = "NA41"
contenu[42] = "NA42"
contenu[43] = size()
#contenu[43] = "NA43"
ss = retour_sock(HOST, PORT, "SS")
contenu[44] = ss[0]
contenu[45] = ss[1]
exterieur = retour_sock(HOST, PORT, "EX")
contenu[46] = exterieur[0]
contenu[47] = "NA"
contenu[48] = ZambrettiText(ZambrettiCode(float(pressure), 10, 8, float(contenu[18])))
contenu[49] = "1"
contenu[50] = "NA"
contenu[51] = VENT("FR",arduino[3])
contenu[52] = "NA"
contenu[53] = "NA"
contenu[54] = "NA"
contenu[55] = tempss
contenu[56] = "NA"
contenu[57] = "NA"
contenu[58] = "END"


file = open(FILE, "w")
for element in contenu:
  file.write("%s " % element)
file.close()

#BASE =  "http://192.168.1.5/emoncms/input/post.json?node1&csv=%s,%s,%s&apikey=79db7b521aec410afc918a92bee06ccd" % (contenu[2], contenu[3], contenu[10])
#urllib2.urlopen(BASE)

#SMS = "/usr/local/bin/googalert \"Temperature en alerte sur ubuntu de %s\" \"Temperature interieure de %s\" " % (contenu[22], contenu[22])
SMS = "curl -s -i -k \"https://smsapi.free-mobile.fr/sendmsg?user=92715699&pass=7kazZsRAgnPWd1&msg=Temperature en alerte %s\" " % contenu[22]

if (float(indoor_temp) < float (SEUIL)):
#   envoi_mail(indoor_temp)
   if not(os.path.isfile("/var/www/html/WC/sms.flag")):
	os.system("%s" % SMS)
	flag=open("/var/www/html/WC/sms.flag","w")
	flag.write("Debut Alarme %s %s\n" % (contenu[0],contenu[1]))
	flag.close()
else:
   if (os.path.isfile("/var/www/html/WC/sms.flag")):
	os.remove("/var/www/html/WC/sms.flag")

 
file = open(FILE2, "w")
file.write("<?xml version=\"1.0\" encoding=\"ISO-8859-15\" ?>\n")
file.write("<maintag>\n")
file.write("<misc>\n")
file.write("<data misc=\"refresh_time\">%s %s</data>\n" % (contenu[0],contenu[1]))
file.write("</misc>\n")
file.write("<misc>\n")
file.write("<data misc=\"forecast_nr\">25</data>\n")
file.write("</misc>\n")
file.write("<realtime>\n")
file.write("<data misc=\"location\">Bourgoin-Jallieu</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"forecast_text\">Showery early, improving</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"temp\">%s C</data>\n" % outdoor_temp)
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"intemp\">%s C</data>\n" % indoor_temp)
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"hum\">%s </data>\n" % outdoor_humidity)
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"inhum\">%s </data>\n" % indoor_humidity)
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"press\">%s hPa</data>\n" % pressure)
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"tempunit\">&deg;C</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"pressunit\">hPa</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"rainunit\">mm</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"windunit\">kmh</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"rfall\">12</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"rhour\">14</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"rrate\">13</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"wgust\">23</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"wdir\">N</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data realtime=\"windspeed\">%s</data>\n" % arduino[2])
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data today=\"today_temp_low\">%s C</data>\n" % contenu[28])
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data today=\"today_temp_high\">%s C</data>\n" % contenu[26])
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data today=\"today_press_low\">%s hPa</data>\n" % contenu[36])
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data today=\"today_press_high\">%s hPa</data>\n" % contenu[34])
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data today=\"today_hour_rainfall\">NA</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data today=\"today_rainfall\">NA</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data today=\"today_max_windspeed\">NA</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data today=\"today_max_windgust\">NA</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data yesterday=\"yesterday_temp_low\">-25 C</data>\n")
file.write("</realtime>\n")
file.write("<realtime>\n")
file.write("<data yesterday=\"yesterday_temp_high\">100 C</data>\n")
file.write("</realtime>\n")

file.write("</maintag>\n")
file.close()
