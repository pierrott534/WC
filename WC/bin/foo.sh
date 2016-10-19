#!/bin/sh

for i in `ps -ef |grep foo|grep -v "grep"|grep python|awk '{print $2}'`
do
	kill -9 $i
done
/usr/bin/python /var/www/html/WC/bin/foo.py
php /var/www/html/WC/bin/ImportCumulusFile.php file=/var/www/html/WC/realtime.txt table=Bourgoin type=realtime key=letmein
