#!/bin/sh
set -x
exec > /var/log/Enigma2_Bouquet_Picon_Update.log 2>&1
#DESCRIPTION=Downloads, Installs & Reloads the latest Enigma2 Bouquets & Picons

#Transfer script to /usr/script and chmod 755 
#A log file will be created in /var/log

#Change the URL to point to your Bouquet tar.gz file
#BQ="http://www.xxxx.co.uk/xxxx/enigma2.tar.gz"
BP="http://upload.sat-universum.de/picon.tar.gz"

## Bouquet Download, Installation + Reload ##
#cd /tmp/
#wget $BQ
#chmod 755 /tmp/enigma2.tar.gz
#tar -xzvf enigma2.tar.gz

#cd /tmp/enigma2
#rm -rf /etc/tuxbox/satellites.xml
#mv /tmp/enigma2/satellites.xml /etc/tuxbox/

#cd /etc/enigma2
#rm -rf *.tv
#rm -rf *.radio
#rm -rf blacklist
#rm -rf lamedb
#mv /tmp/enigma2/* /etc/enigma2#

#rm -rf /tmp/enigma2
#rm -rf /tmp/enigma2.tar.gz

#wget -qO - http://127.0.0.1/web/servicelistreload?mode=1
#wget -qO - http://127.0.0.1/web/servicelistreload?mode=2

## Picon Installation ##
cd /tmp/
wget $BP
chmod 755 /tmp/picon.tar.gz
/sbin/tar -xzvf picon.tar.gz
rm -rf /hdd/picon/
mv /tmp/picon/ /hdd/

rm -rf /tmp/picon.tar.gz

ln -s /hdd/picon /usr/share/enigma2/picon > /dev/null 2>&1