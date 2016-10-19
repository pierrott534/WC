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

def VENT(wind):
	if wind == "0":
	  windstr="N"
	elif wind == "23":
	  windstr="NNO"
	elif wind == "45":
	  windstr="NO"
	elif wind == "68":
	  windstr="ONO"
	elif wind == "90":
	  windstr="O"
	elif wind == 113:
	  windstr="OSO"
	elif wind == 135:
	  windstr="SO"
	elif wind == 158:
	  windstr="SSO"
	elif wind == 180:
	  windstr="S"
	elif wind == 203:
	  windstr="SSE"
	elif wind == 225:
	  windstr="SE"
	elif wind == 248:
	  windstr="ESE"
	elif wind == 270:
	  windstr="E"
	elif wind == 293:
	  windstr="ENE"
	elif wind == 315:
	  windstr="NE"
	elif wind == 338:
	  windstr="NNE"

	print windstr

wind="0"
VENT(wind)
print wind
